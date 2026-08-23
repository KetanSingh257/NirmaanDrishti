"""Request / response schemas for the three intelligence engines."""

from datetime import date as Date

from pydantic import BaseModel, Field


class CostPredictRequest(BaseModel):
    original_cost_cr: float = Field(..., gt=0)
    revised_cost_cr: float = Field(..., gt=0)
    current_expenditure_cr: float = Field(..., ge=0)
    physical_progress_pct: float = Field(..., ge=0, le=100)
    previous_progress: float = Field(0, ge=0, le=100)
    previous_expenditure: float = Field(0, ge=0)
    project_age_days: int = Field(..., ge=0)
    days_to_original_completion: int = 0
    days_overdue: int = Field(0, ge=0)
    agency: str = "UNKNOWN"
    state: str = "UNKNOWN"
    project_id: int | None = None


class CostPredictResponse(BaseModel):
    predicted_expenditure_cr: float
    current_expenditure_cr: float
    predicted_overrun_cr: float
    overrun_percentage: float
    risk_level: str
    risk_score: float
    confidence_score: float
    model_name: str
    explanations: list[str] = Field(default_factory=list)
    used_real_model: bool = False


class TimePredictRequest(BaseModel):
    physical_progress_pct: float = Field(..., ge=0, le=100)
    previous_progress: float = Field(0, ge=0, le=100)
    project_age_days: int = Field(..., ge=0)
    days_to_original_completion: int = 0
    days_overdue: int = Field(0, ge=0)
    original_cost_cr: float = Field(..., gt=0)
    revised_cost_cr: float = Field(..., gt=0)
    start_date: Date | None = None
    original_completion_date: Date | None = None
    agency: str = "UNKNOWN"
    state: str = "UNKNOWN"
    project_id: int | None = None


class TimePredictResponse(BaseModel):
    predicted_delay_days: int
    estimated_completion_date: Date
    delay_probability: float
    remaining_days: int
    risk_level: str
    risk_score: float
    confidence_score: float
    model_name: str
    explanations: list[str] = Field(default_factory=list)
    used_real_model: bool = False


class HistoryPoint(BaseModel):
    date: Date
    physical_progress_pct: float
    expenditure_cr: float


class TrendAnalyzeRequest(BaseModel):
    history: list[HistoryPoint]


class TrendAnalyzeResponse(BaseModel):
    trend: str
    trend_score: float
    progress_velocity: float
    expenditure_velocity: float
    cost_efficiency: float
    progress_slowdown: float
    expenditure_acceleration: float
    risk_level: str
    risk_score: float
    insights: list[str] = Field(default_factory=list)
    series: list[HistoryPoint] = Field(default_factory=list)
