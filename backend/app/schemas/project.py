"""Pydantic schemas for projects and history."""

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class ProjectUpdateOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    update_date: date
    physical_progress_pct: float
    expenditure_cr: float
    remarks: str | None = None


class ProjectBase(BaseModel):
    project_name: str
    project_code: str
    state: str
    agency: str
    sector: str
    description: str | None = None
    original_cost_cr: float
    revised_cost_cr: float
    current_expenditure_cr: float
    physical_progress_pct: float
    start_date: date
    original_completion_date: date
    revised_completion_date: date | None = None
    status: str
    location: str | None = None


class ProjectOut(ProjectBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime | None = None
    updated_at: datetime | None = None

    project_age_days: int = 0
    days_overdue: int = 0
    days_to_original_completion: int = 0
    previous_progress: float = 0.0
    previous_expenditure: float = 0.0


class ProjectListItem(ProjectOut):
    overall_risk_score: float = 0.0
    health_status: str = "WATCH"
    cost_risk_level: str = "MEDIUM"
    time_risk_level: str = "MEDIUM"
    trend: str = "STABLE"


class ProjectDetail(ProjectListItem):
    updates: list[ProjectUpdateOut] = Field(default_factory=list)


class ProjectListResponse(BaseModel):
    items: list[ProjectListItem]
    total: int
    page: int
    limit: int
    pages: int


class ProjectOption(BaseModel):
    id: int
    project_name: str


class FilterOptions(BaseModel):
    states: list[str]
    agencies: list[str]
    sectors: list[str]
    statuses: list[str]
    risk_levels: list[str]
