from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.intelligence import DashboardResponse
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])
service = AnalyticsService()


@router.get("", response_model=DashboardResponse)
def get_dashboard(db: Session = Depends(get_db)) -> DashboardResponse:
    return service.dashboard(db)
