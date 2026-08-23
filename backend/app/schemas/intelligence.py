"""Combined intelligence, dashboard, analytics, and risk schemas."""

from datetime import date as Date

from pydantic import BaseModel, Field

from app.schemas.prediction import (
    CostPredictResponse,
    TimePredictResponse,
    TrendAnalyzeResponse,
)
from app.schemas.project import ProjectListItem


class IntelligenceResponse(BaseModel):
    project_id: int
    project_name: str
    overall_risk_score: float
    health_status: str
    cost: CostPredictResponse
    time: TimePredictResponse
    trend: TrendAnalyzeResponse
    key_insights: list[str] = Field(default_factory=list)
    weights: dict[str, float] = Field(default_factory=dict)


class KpiCard(BaseModel):
    label: str
    value: float | int | str
    delta: float | None = None
    delta_label: str | None = None
    sparkline: list[float] = Field(default_factory=list)


class DashboardResponse(BaseModel):
    total_projects: int
    projects_at_risk: int
    total_project_value_cr: float
    potential_overrun_cr: float
    healthy: int
    watch: int
    at_risk: int
    critical: int
    risk_trend: list[dict]
    cost_vs_progress: list[dict]
    critical_projects: list[ProjectListItem]
    health_distribution: list[dict]
    recent_alerts: list[dict]


class RiskItem(BaseModel):
    project_id: int
    project_name: str
    project_code: str
    state: str
    agency: str
    sector: str
    physical_progress_pct: float
    overall_risk_score: float
    health_status: str
    cost_risk_level: str
    time_risk_level: str
    trend: str
    reasons: list[str]
    original_cost_cr: float
    current_expenditure_cr: float


class RiskListResponse(BaseModel):
    items: list[RiskItem]
    total: int
    critical_count: int
    at_risk_count: int


class AnalyticsOverview(BaseModel):
    state_risk: list[dict]
    agency_performance: list[dict]
    sector_distribution: list[dict]
    cost_overruns: list[dict]
    delay_distribution: list[dict]
    health_distribution: list[dict]
    risk_trends: list[dict]
    progress_vs_expenditure: list[dict]
    top_overruns: list[dict]
    monthly_progress: list[dict]


class TimelinePoint(BaseModel):
    label: str
    at: Date | None = None
    kind: str
