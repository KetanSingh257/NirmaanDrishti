from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.intelligence import RiskItem, RiskListResponse
from app.services.intelligence_service import IntelligenceService
from app.services.project_service import ProjectService, to_out

router = APIRouter(prefix="/api/risks", tags=["risks"])
projects = ProjectService()
intel = IntelligenceService()


@router.get("", response_model=RiskListResponse)
def list_risks(
    state: str | None = None,
    agency: str | None = None,
    focus: str | None = Query(None, description="cost|time|trend|overall"),
    db: Session = Depends(get_db),
) -> RiskListResponse:
    rows = projects.all_with_updates(db)
    items: list[RiskItem] = []
    for p in rows:
        if state and p.state != state:
            continue
        if agency and p.agency != agency:
            continue
        base = to_out(p)
        scores = intel.score_only(db, p)
        status = scores["health_status"]
        if status not in {"AT_RISK", "CRITICAL", "WATCH"}:
            continue
        if focus == "cost" and scores["cost_risk_level"] not in {"HIGH", "CRITICAL"}:
            continue
        if focus == "time" and scores["time_risk_level"] not in {"HIGH", "CRITICAL"}:
            continue
        if focus == "trend" and scores["trend"] not in {"DETERIORATING", "WEAKENING"}:
            continue
        if focus == "overall" and status not in {"AT_RISK", "CRITICAL"}:
            continue
        reasons = scores.get("insights") or []
        items.append(
            RiskItem(
                project_id=p.id,
                project_name=p.project_name,
                project_code=p.project_code,
                state=p.state,
                agency=p.agency,
                sector=p.sector,
                physical_progress_pct=p.physical_progress_pct,
                overall_risk_score=scores["overall_risk_score"],
                health_status=status,
                cost_risk_level=scores["cost_risk_level"],
                time_risk_level=scores["time_risk_level"],
                trend=scores["trend"],
                reasons=reasons[:4],
                original_cost_cr=p.original_cost_cr,
                current_expenditure_cr=p.current_expenditure_cr,
            )
        )

    items.sort(key=lambda x: x.overall_risk_score, reverse=True)
    return RiskListResponse(
        items=items,
        total=len(items),
        critical_count=sum(1 for i in items if i.health_status == "CRITICAL"),
        at_risk_count=sum(1 for i in items if i.health_status == "AT_RISK"),
    )
