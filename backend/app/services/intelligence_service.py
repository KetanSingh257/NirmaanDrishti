"""Intelligence layer — fuses cost, time, and trend engines."""

from __future__ import annotations

from datetime import date

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.project import Project
from app.schemas.intelligence import IntelligenceResponse
from app.schemas.prediction import CostPredictRequest, TimePredictRequest
from app.services.cost_prediction_service import CostPredictionService
from app.services.project_service import ProjectService, derived_fields
from app.services.time_prediction_service import TimePredictionService
from app.services.trend_engine import TrendEngine


def health_from_score(score: float) -> str:
    cfg = get_settings()
    if score <= cfg.healthy_max:
        return "HEALTHY"
    if score <= cfg.watch_max:
        return "WATCH"
    if score <= cfg.at_risk_max:
        return "AT_RISK"
    return "CRITICAL"


class IntelligenceService:
    def __init__(self) -> None:
        self.cost = CostPredictionService()
        self.time = TimePredictionService()
        self.trend = TrendEngine()
        self.projects = ProjectService()

    def evaluate(self, db: Session, project: Project) -> IntelligenceResponse:
        derived = derived_fields(project)
        cost_req = CostPredictRequest(
            original_cost_cr=project.original_cost_cr,
            revised_cost_cr=project.revised_cost_cr,
            current_expenditure_cr=project.current_expenditure_cr,
            physical_progress_pct=project.physical_progress_pct,
            previous_progress=derived["previous_progress"],
            previous_expenditure=derived["previous_expenditure"],
            project_age_days=derived["project_age_days"],
            days_to_original_completion=derived["days_to_original_completion"],
            days_overdue=derived["days_overdue"],
            agency=project.agency,
            state=project.state,
            project_id=project.id,
        )
        time_req = TimePredictRequest(
            physical_progress_pct=project.physical_progress_pct,
            previous_progress=derived["previous_progress"],
            project_age_days=derived["project_age_days"],
            days_to_original_completion=derived["days_to_original_completion"],
            days_overdue=derived["days_overdue"],
            original_cost_cr=project.original_cost_cr,
            revised_cost_cr=project.revised_cost_cr,
            start_date=project.start_date,
            original_completion_date=project.original_completion_date,
            agency=project.agency,
            state=project.state,
            project_id=project.id,
        )
        history = [
            {
                "date": u.update_date,
                "physical_progress_pct": u.physical_progress_pct,
                "expenditure_cr": u.expenditure_cr,
            }
            for u in (project.updates or [])
        ]
        if not history:
            history = [
                {
                    "date": project.start_date,
                    "physical_progress_pct": 0,
                    "expenditure_cr": 0,
                },
                {
                    "date": date.today(),
                    "physical_progress_pct": project.physical_progress_pct,
                    "expenditure_cr": project.current_expenditure_cr,
                },
            ]

        cost = self.cost.predict(cost_req)
        time = self.time.predict(time_req)
        trend = self.trend.analyze(history)

        cfg = get_settings()
        overall = (
            cost.risk_score * cfg.cost_risk_weight
            + time.risk_score * cfg.time_risk_weight
            + trend.risk_score * cfg.trend_risk_weight
        )
        overall = round(overall, 1)
        status = health_from_score(overall)

        insights = self._compose_insights(cost, time, trend, status)
        return IntelligenceResponse(
            project_id=project.id,
            project_name=project.project_name,
            overall_risk_score=overall,
            health_status=status,
            cost=cost,
            time=time,
            trend=trend,
            key_insights=insights,
            weights={
                "cost": cfg.cost_risk_weight,
                "time": cfg.time_risk_weight,
                "trend": cfg.trend_risk_weight,
            },
        )

    def score_only(self, db: Session, project: Project) -> dict:
        intel = self.evaluate(db, project)
        return {
            "overall_risk_score": intel.overall_risk_score,
            "health_status": intel.health_status,
            "cost_risk_level": intel.cost.risk_level,
            "time_risk_level": intel.time.risk_level,
            "trend": intel.trend.trend,
            "cost_risk_score": intel.cost.risk_score,
            "time_risk_score": intel.time.risk_score,
            "trend_risk_score": intel.trend.risk_score,
            "predicted_overrun_cr": intel.cost.predicted_overrun_cr,
            "predicted_delay_days": intel.time.predicted_delay_days,
            "insights": intel.key_insights,
        }

    def _compose_insights(self, cost, time, trend, status) -> list[str]:
        notes: list[str] = []
        if cost.risk_level in {"HIGH", "CRITICAL"}:
            notes.append(
                f"High probability of cost overrun — predicted extra ₹{cost.predicted_overrun_cr:,.0f} Cr "
                f"({cost.overrun_percentage:.1f}%)."
            )
        if time.risk_level in {"HIGH", "CRITICAL"}:
            notes.append(
                f"Project is predicted to slip by {time.predicted_delay_days} days "
                f"(completion ~ {time.estimated_completion_date.isoformat()})."
            )
        if trend.trend in {"DETERIORATING", "WEAKENING"}:
            notes.append("Performance trend is deteriorating across recent reporting windows.")
        notes.extend(trend.insights[:2])
        if status == "HEALTHY":
            notes.append("Overall health is within acceptable bounds — continue routine monitoring.")
        # de-duplicate while preserving order
        seen: set[str] = set()
        unique: list[str] = []
        for n in notes:
            if n not in seen:
                seen.add(n)
                unique.append(n)
        return unique[:6]
