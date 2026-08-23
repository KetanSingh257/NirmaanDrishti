from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.intelligence import IntelligenceResponse
from app.services.intelligence_service import IntelligenceService
from app.services.project_service import ProjectService

router = APIRouter(prefix="/api/intelligence", tags=["intelligence"])
intel = IntelligenceService()
projects = ProjectService()


@router.get("/{project_id}", response_model=IntelligenceResponse)
def get_intelligence(project_id: int, db: Session = Depends(get_db)) -> IntelligenceResponse:
    project = projects.get_or_404(db, project_id)
    return intel.evaluate(db, project)
