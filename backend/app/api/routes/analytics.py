from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.intelligence import AnalyticsOverview
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/api/analytics", tags=["analytics"])
service = AnalyticsService()


@router.get("/overview", response_model=AnalyticsOverview)
def analytics_overview(db: Session = Depends(get_db)) -> AnalyticsOverview:
    return service.overview(db)
