"""Project query helpers and derived-field computation."""

from __future__ import annotations

from datetime import date
from math import ceil
from typing import Any

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.models.project import Project
from app.models.project_update import ProjectUpdate
from app.schemas.project import (
    FilterOptions,
    ProjectListItem,
    ProjectListResponse,
    ProjectOut,
)


def derived_fields(project: Project) -> dict[str, Any]:
    today = date.today()
    age = max((today - project.start_date).days, 0)
    days_to = (project.original_completion_date - today).days
    overdue = max(-days_to, 0) if days_to < 0 else 0

    updates = list(project.updates or [])
    prev_progress = 0.0
    prev_exp = 0.0
    if len(updates) >= 2:
        prev_progress = updates[-2].physical_progress_pct
        prev_exp = updates[-2].expenditure_cr
    elif len(updates) == 1:
        prev_progress = max(project.physical_progress_pct - 3, 0)
        prev_exp = max(project.current_expenditure_cr * 0.9, 0)

    return {
        "project_age_days": age,
        "days_to_original_completion": days_to,
        "days_overdue": overdue,
        "previous_progress": prev_progress,
        "previous_expenditure": prev_exp,
    }


def to_out(project: Project) -> dict[str, Any]:
    data = {
        "id": project.id,
        "project_name": project.project_name,
        "project_code": project.project_code,
        "state": project.state,
        "agency": project.agency,
        "sector": project.sector,
        "description": project.description,
        "original_cost_cr": project.original_cost_cr,
        "revised_cost_cr": project.revised_cost_cr,
        "current_expenditure_cr": project.current_expenditure_cr,
        "physical_progress_pct": project.physical_progress_pct,
        "start_date": project.start_date,
        "original_completion_date": project.original_completion_date,
        "revised_completion_date": project.revised_completion_date,
        "status": project.status,
        "location": project.location,
        "created_at": project.created_at,
        "updated_at": project.updated_at,
    }
    data.update(derived_fields(project))
    return data


class ProjectService:
    def get(self, db: Session, project_id: int) -> Project | None:
        stmt = (
            select(Project)
            .options(selectinload(Project.updates), selectinload(Project.predictions))
            .where(Project.id == project_id)
        )
        return db.execute(stmt).scalar_one_or_none()

    def get_or_404(self, db: Session, project_id: int) -> Project:
        project = self.get(db, project_id)
        if project is None:
            from fastapi import HTTPException

            raise HTTPException(status_code=404, detail="Project not found")
        return project

    def list_projects(
        self,
        db: Session,
        *,
        page: int = 1,
        limit: int = 20,
        state: str | None = None,
        agency: str | None = None,
        sector: str | None = None,
        risk_level: str | None = None,
        status: str | None = None,
        search: str | None = None,
        sort: str = "risk_desc",
    ) -> tuple[list[Project], int]:
        stmt = select(Project).options(selectinload(Project.updates))
        count_stmt = select(func.count(Project.id))

        filters = []
        if state:
            filters.append(Project.state == state)
        if agency:
            filters.append(Project.agency == agency)
        if sector:
            filters.append(Project.sector == sector)
        if status:
            filters.append(Project.status == status)
        if search:
            like = f"%{search.strip()}%"
            filters.append(
                or_(
                    Project.project_name.ilike(like),
                    Project.project_code.ilike(like),
                    Project.agency.ilike(like),
                    Project.state.ilike(like),
                    Project.sector.ilike(like),
                )
            )
        if filters:
            stmt = stmt.where(*filters)
            count_stmt = count_stmt.where(*filters)

        if sort == "expenditure_desc":
            stmt = stmt.order_by(Project.current_expenditure_cr.desc())
        elif sort == "expenditure_asc":
            stmt = stmt.order_by(Project.current_expenditure_cr.asc())
        elif sort == "progress_desc":
            stmt = stmt.order_by(Project.physical_progress_pct.desc())
        elif sort == "progress_asc":
            stmt = stmt.order_by(Project.physical_progress_pct.asc())
        elif sort == "name":
            stmt = stmt.order_by(Project.project_name.asc())
        else:
            stmt = stmt.order_by(Project.revised_cost_cr.desc())

        total = db.execute(count_stmt).scalar_one()
        rows = (
            db.execute(stmt.offset((page - 1) * limit).limit(limit)).scalars().all()
        )
        return list(rows), int(total)

    def all_with_updates(self, db: Session) -> list[Project]:
        stmt = select(Project).options(selectinload(Project.updates)).order_by(Project.id)
        return list(db.execute(stmt).scalars().all())

    def options(self, db: Session, search: str | None = None) -> list[dict[str, Any]]:
        stmt = select(Project.id, Project.project_name).order_by(Project.project_name, Project.id)
        if search and search.strip():
            stmt = stmt.where(Project.project_name.ilike(f"%{search.strip()}%"))
        return [
            {"id": project_id, "project_name": project_name}
            for project_id, project_name in db.execute(stmt).all()
        ]

    def history(self, db: Session, project_id: int) -> list[ProjectUpdate]:
        stmt = (
            select(ProjectUpdate)
            .where(ProjectUpdate.project_id == project_id)
            .order_by(ProjectUpdate.update_date.asc())
        )
        return list(db.execute(stmt).scalars().all())

    def filter_options(self, db: Session) -> FilterOptions:
        def col_values(column) -> list[str]:
            rows = db.execute(select(column).distinct().order_by(column)).scalars().all()
            return [r for r in rows if r]

        return FilterOptions(
            states=col_values(Project.state),
            agencies=col_values(Project.agency),
            sectors=col_values(Project.sector),
            statuses=col_values(Project.status),
            risk_levels=["HEALTHY", "WATCH", "AT_RISK", "CRITICAL"],
        )

    def enrich(self, db: Session, project: Project) -> dict[str, Any]:
        from app.services.intelligence_service import IntelligenceService

        base = to_out(project)
        scores = IntelligenceService().score_only(db, project)
        base.update(scores)
        return base

    def enrich_many(self, db: Session, projects: list[Project]) -> list[dict[str, Any]]:
        intel = None
        from app.services.intelligence_service import IntelligenceService

        intel = IntelligenceService()
        out = []
        for p in projects:
            row = to_out(p)
            row.update(intel.score_only(db, p))
            out.append(row)
        return out

    def paginated(
        self,
        db: Session,
        **kwargs: Any,
    ) -> ProjectListResponse:
        risk_level = kwargs.pop("risk_level", None)
        sort = kwargs.get("sort", "risk_desc")
        page = kwargs.get("page", 1)
        limit = kwargs.get("limit", 20)

        # Pull a wider set when we need in-memory risk sort / filter
        needs_scores = sort in {"risk_desc", "risk_asc"} or bool(risk_level)
        if needs_scores:
            kwargs["page"] = 1
            kwargs["limit"] = 500
            kwargs["sort"] = "name" if sort.startswith("risk") else sort

        rows, total = self.list_projects(db, **kwargs)
        items = self.enrich_many(db, rows)

        if risk_level:
            items = [i for i in items if i["health_status"] == risk_level]
            total = len(items)

        if sort == "risk_desc":
            items.sort(key=lambda x: x["overall_risk_score"], reverse=True)
        elif sort == "risk_asc":
            items.sort(key=lambda x: x["overall_risk_score"])

        if needs_scores:
            pages = max(ceil(total / limit), 1) if limit else 1
            start = (page - 1) * limit
            items = items[start : start + limit]
        else:
            pages = max(ceil(total / limit), 1) if limit else 1

        return ProjectListResponse(
            items=[ProjectListItem(**i) for i in items],
            total=total,
            page=page,
            limit=limit,
            pages=pages,
        )
