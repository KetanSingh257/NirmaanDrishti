import axios from 'axios'
import type {
  AnalyticsOverview,
  CostPredictPayload,
  CostPrediction,
  DashboardData,
  FilterOptions,
  Intelligence,
  Project,
  ProjectOption,
  ProjectListResponse,
  ProjectUpdate,
  RiskListResponse,
  TimePredictPayload,
  TimePrediction,
  TrendAnalysis,
} from './types'

export const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
})

export const fetchDashboard = async () => {
  const { data } = await api.get<DashboardData>('/dashboard')
  return data
}

export const fetchProjects = async (params: Record<string, string | number | undefined>) => {
  const { data } = await api.get<ProjectListResponse>('/projects', { params })
  return data
}

export const fetchProjectOptions = async () => {
  const { data } = await api.get<ProjectOption[]>('/projects/options')
  return data
}

export const fetchFilters = async () => {
  const { data } = await api.get<FilterOptions>('/projects/filters')
  return data
}

export const fetchProject = async (id: number | string) => {
  const { data } = await api.get<Project>(`/projects/${id}`)
  return data
}

export const fetchHistory = async (id: number | string) => {
  const { data } = await api.get<ProjectUpdate[]>(`/projects/${id}/history`)
  return data
}

export const fetchIntelligence = async (id: number | string) => {
  const { data } = await api.get<Intelligence>(`/intelligence/${id}`)
  return data
}

export const predictCost = async (payload: CostPredictPayload) => {
  const { data } = await api.post<CostPrediction>('/predict/cost', payload)
  return data
}

export const predictTime = async (payload: TimePredictPayload) => {
  const { data } = await api.post<TimePrediction>('/predict/time', payload)
  return data
}

export const analyzeTrend = async (id: number | string) => {
  const { data } = await api.get<TrendAnalysis>(`/analyze/trend/${id}`)
  return data
}

export const fetchRisks = async (params?: Record<string, string | undefined>) => {
  const { data } = await api.get<RiskListResponse>('/risks', { params })
  return data
}

export const fetchAnalytics = async () => {
  const { data } = await api.get<AnalyticsOverview>('/analytics/overview')
  return data
}

export const fetchHealth = async () => {
  const { data } = await api.get<{ status: string; service: string; version: string }>('/health')
  return data
}
