from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.prediction import (
    CostPredictRequest,
    CostPredictResponse,
    TimePredictRequest,
    TimePredictResponse,
    TrendAnalyzeRequest,
    TrendAnalyzeResponse,
)
from app.services.cost_prediction_service import CostPredictionService
from app.services.project_service import ProjectService
from app.services.time_prediction_service import TimePredictionService
from app.services.trend_engine import TrendEngine

router = APIRouter(prefix="/api", tags=["predictions"])
cost_svc = CostPredictionService()
time_svc = TimePredictionService()
trend_svc = TrendEngine()
projects = ProjectService()


@router.post("/predict/cost", response_model=CostPredictResponse)
def predict_cost(payload: CostPredictRequest) -> CostPredictResponse:
    return cost_svc.predict(payload)


@router.post("/predict/time", response_model=TimePredictResponse)
def predict_time(payload: TimePredictRequest) -> TimePredictResponse:
    return time_svc.predict(payload)


@router.post("/analyze/trend", response_model=TrendAnalyzeResponse)
def analyze_trend_payload(payload: TrendAnalyzeRequest) -> TrendAnalyzeResponse:
    return trend_svc.analyze(payload.history)


@router.get("/analyze/trend/{project_id}", response_model=TrendAnalyzeResponse)
def analyze_trend(project_id: int, db: Session = Depends(get_db)) -> TrendAnalyzeResponse:
    project = projects.get_or_404(db, project_id)
    history = [
        {
            "date": u.update_date,
            "physical_progress_pct": u.physical_progress_pct,
            "expenditure_cr": u.expenditure_cr,
        }
        for u in project.updates
    ]
    return trend_svc.analyze(history)
