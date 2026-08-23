from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.project import (
    FilterOptions,
    ProjectDetail,
    ProjectOption,
    ProjectListResponse,
    ProjectUpdateOut,
)
from app.services.project_service import ProjectService, to_out

router = APIRouter(prefix="/api/projects", tags=["projects"])
service = ProjectService()


@router.get("", response_model=ProjectListResponse)
def list_projects(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    state: str | None = None,
    agency: str | None = None,
    sector: str | None = None,
    risk_level: str | None = None,
    status: str | None = None,
    search: str | None = None,
    sort: str = "risk_desc",
    db: Session = Depends(get_db),
) -> ProjectListResponse:
    return service.paginated(
        db,
        page=page,
        limit=limit,
        state=state,
        agency=agency,
        sector=sector,
        risk_level=risk_level,
        status=status,
        search=search,
        sort=sort,
    )


@router.get("/filters", response_model=FilterOptions)
def filters(db: Session = Depends(get_db)) -> FilterOptions:
    return service.filter_options(db)


@router.get("/options", response_model=list[ProjectOption])
def project_options(
    search: str | None = None,
    db: Session = Depends(get_db),
) -> list[ProjectOption]:
    options = service.options(db, search)
    return [ProjectOption(**option) for option in options]


@router.get("/{project_id}", response_model=ProjectDetail)
def get_project(project_id: int, db: Session = Depends(get_db)) -> ProjectDetail:
    project = service.get_or_404(db, project_id)
    data = service.enrich(db, project)
    data["updates"] = project.updates
    return ProjectDetail(**data)


@router.get("/{project_id}/history", response_model=list[ProjectUpdateOut])
def project_history(project_id: int, db: Session = Depends(get_db)) -> list[ProjectUpdateOut]:
    service.get_or_404(db, project_id)
    return service.history(db, project_id)
