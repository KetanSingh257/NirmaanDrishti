export type HealthStatus = 'HEALTHY' | 'WATCH' | 'AT_RISK' | 'CRITICAL'
export type RiskLevel = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL'
export type TrendDirection = 'IMPROVING' | 'STABLE' | 'WEAKENING' | 'DETERIORATING' | 'INSUFFICIENT_DATA'

export interface ProjectUpdate {
  id: number
  project_id: number
  update_date: string
  physical_progress_pct: number
  expenditure_cr: number
  remarks?: string | null
}

export interface Project {
  id: number
  project_name: string
  project_code: string
  state: string
  agency: string
  sector: string
  description?: string | null
  original_cost_cr: number
  revised_cost_cr: number
  current_expenditure_cr: number
  physical_progress_pct: number
  start_date: string
  original_completion_date: string
  revised_completion_date?: string | null
  status: string
  location?: string | null
  project_age_days: number
  days_overdue: number
  days_to_original_completion: number
  previous_progress: number
  previous_expenditure: number
  overall_risk_score: number
  health_status: HealthStatus
  cost_risk_level: RiskLevel
  time_risk_level: RiskLevel
  trend: TrendDirection
  updates?: ProjectUpdate[]
}

export interface ProjectListResponse {
  items: Project[]
  total: number
  page: number
  limit: number
  pages: number
}

export interface ProjectOption {
  id: number
  project_name: string
}

export interface FilterOptions {
  states: string[]
  agencies: string[]
  sectors: string[]
  statuses: string[]
  risk_levels: string[]
}

export interface CostPrediction {
  predicted_expenditure_cr: number
  current_expenditure_cr: number
  predicted_overrun_cr: number
  overrun_percentage: number
  risk_level: RiskLevel
  risk_score: number
  confidence_score: number
  model_name: string
  explanations: string[]
  used_real_model: boolean
}

export interface TimePrediction {
  predicted_delay_days: number
  estimated_completion_date: string
  delay_probability: number
  remaining_days: number
  risk_level: RiskLevel
  risk_score: number
  confidence_score: number
  model_name: string
  explanations: string[]
  used_real_model: boolean
}

export interface TrendAnalysis {
  trend: TrendDirection
  trend_score: number
  progress_velocity: number
  expenditure_velocity: number
  cost_efficiency: number
  progress_slowdown: number
  expenditure_acceleration: number
  risk_level: RiskLevel
  risk_score: number
  insights: string[]
  series: { date: string; physical_progress_pct: number; expenditure_cr: number }[]
}

export interface Intelligence {
  project_id: number
  project_name: string
  overall_risk_score: number
  health_status: HealthStatus
  cost: CostPrediction
  time: TimePrediction
  trend: TrendAnalysis
  key_insights: string[]
  weights: Record<string, number>
}

export interface DashboardData {
  total_projects: number
  projects_at_risk: number
  total_project_value_cr: number
  potential_overrun_cr: number
  healthy: number
  watch: number
  at_risk: number
  critical: number
  risk_trend: Array<Record<string, string | number>>
  cost_vs_progress: Array<Record<string, string | number>>
  critical_projects: Project[]
  health_distribution: { name: string; value: number; key: string }[]
  recent_alerts: {
    project_id: number
    project_name: string
    health_status: string
    score: number
    message: string
  }[]
}

export interface RiskItem {
  project_id: number
  project_name: string
  project_code: string
  state: string
  agency: string
  sector: string
  physical_progress_pct: number
  overall_risk_score: number
  health_status: HealthStatus
  cost_risk_level: RiskLevel
  time_risk_level: RiskLevel
  trend: TrendDirection
  reasons: string[]
  original_cost_cr: number
  current_expenditure_cr: number
}

export interface RiskListResponse {
  items: RiskItem[]
  total: number
  critical_count: number
  at_risk_count: number
}

export interface AnalyticsOverview {
  state_risk: Array<Record<string, string | number>>
  agency_performance: Array<Record<string, string | number>>
  sector_distribution: Array<Record<string, string | number>>
  cost_overruns: Array<Record<string, string | number>>
  delay_distribution: Array<Record<string, string | number>>
  health_distribution: { name: string; value: number; key: string }[]
  risk_trends: Array<Record<string, string | number>>
  progress_vs_expenditure: Array<Record<string, string | number>>
  top_overruns: Array<Record<string, string | number>>
  monthly_progress: Array<Record<string, string | number>>
}

export interface CostPredictPayload {
  original_cost_cr: number
  revised_cost_cr: number
  current_expenditure_cr: number
  physical_progress_pct: number
  previous_progress: number
  previous_expenditure: number
  project_age_days: number
  days_to_original_completion: number
  days_overdue: number
  agency: string
  state: string
}

export interface TimePredictPayload {
  physical_progress_pct: number
  previous_progress: number
  project_age_days: number
  days_to_original_completion: number
  days_overdue: number
  original_cost_cr: number
  revised_cost_cr: number
  agency: string
  state: string
}
