import { Navigate, Route, Routes } from 'react-router-dom'
import AppLayout from './components/layout/AppLayout'
import Landing from './pages/Landing'
import Dashboard from './pages/Dashboard'
import Projects from './pages/Projects'
import ProjectDetail from './pages/ProjectDetail'
import CostAnalysis from './pages/CostAnalysis'
import TimeAnalysis from './pages/TimeAnalysis'
import TrendAnalysis from './pages/TrendAnalysis'
import RiskMonitor from './pages/RiskMonitor'
import Analytics from './pages/Analytics'
import Settings from './pages/Settings'

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/app/dashboard" replace />} />
      <Route element={<AppLayout />}>
        <Route path="/app" element={<Navigate to="/app/dashboard" replace />} />
        <Route path="/app/dashboard" element={<Dashboard />} />
        <Route path="/app/projects" element={<Projects />} />
        <Route path="/app/projects/:id" element={<ProjectDetail />} />
        <Route path="/app/intelligence/cost" element={<CostAnalysis />} />
        <Route path="/app/intelligence/time" element={<TimeAnalysis />} />
        <Route path="/app/intelligence/trend" element={<TrendAnalysis />} />
        <Route path="/app/risks" element={<RiskMonitor />} />
        <Route path="/app/analytics" element={<Analytics />} />
        <Route path="/app/settings" element={<Settings />} />
      </Route>
      <Route path="*" element={<Navigate to="/app/dashboard" replace />} />
    </Routes>
  )
}
