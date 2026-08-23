import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import {
  Area,
  AreaChart,
  CartesianGrid,
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Scatter,
  ScatterChart,
  Tooltip,
  XAxis,
  YAxis,
  ZAxis,
} from 'recharts'
import { AlertTriangle, IndianRupee, Landmark, ShieldAlert } from 'lucide-react'
import { fetchDashboard } from '../lib/api'
import { compactInr, inrCr, pct } from '../lib/format'
import { healthTone } from '../lib/utils'
import { Card, CardHeader } from '../components/ui/Card'
import { HealthBadge } from '../components/ui/Badge'
import { ErrorState, LoadingState } from '../components/ui/States'
import { AnimatedNumber } from '../components/shared/AnimatedNumber'
import { PageHeader } from '../components/shared/PageHeader'

const COLORS: Record<string, string> = {
  HEALTHY: '#4aa87a',
  WATCH: '#d4a017',
  AT_RISK: '#fb923c',
  CRITICAL: '#e06b6b',
}

export default function Dashboard() {
  const { data, isLoading, isError } = useQuery({ queryKey: ['dashboard'], queryFn: fetchDashboard })
  if (isLoading) return <LoadingState label="Syncing command picture…" />
  if (isError || !data) return <ErrorState />

  const kpis = [
    { label: 'Total Projects', value: data.total_projects, icon: Landmark, format: (n: number) => Math.round(n).toLocaleString('en-IN') },
    { label: 'Projects at Risk', value: data.projects_at_risk, icon: ShieldAlert, format: (n: number) => Math.round(n).toLocaleString('en-IN') },
    { label: 'Total Project Value', value: data.total_project_value_cr, icon: IndianRupee, format: (n: number) => compactInr(n) },
    { label: 'Potential Overrun', value: data.potential_overrun_cr, icon: AlertTriangle, format: (n: number) => compactInr(n) },
  ]

  return (
    <div>
      <PageHeader
        eyebrow="Command center"
        title="Portfolio intelligence"
        subtitle="Live fusion of cost, schedule and trend engines across the monitored programme."
      />

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {kpis.map((k, i) => (
          <motion.div
            key={k.label}
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.06 }}
            className="glass group rounded-xl p-5 transition hover:border-parchment-300/25"
          >
            <div className="mb-4 flex items-center justify-between">
              <p className="font-mono text-[10px] uppercase tracking-[0.18em] text-parchment-200/50">{k.label}</p>
              <k.icon className="h-4 w-4 text-parchment-300/70" />
            </div>
            <p className="font-display text-2xl font-semibold tabular-nums sm:text-3xl">
              <AnimatedNumber value={k.value} format={k.format} />
            </p>
          </motion.div>
        ))}
      </div>

      <div className="mt-6 grid gap-4 lg:grid-cols-5">
        <Card className="lg:col-span-2">
          <CardHeader eyebrow="Distribution" title="Project health" />
          <div className="flex items-center gap-4 p-5">
            <div className="h-48 w-48">
              <ResponsiveContainer>
                <PieChart>
                  <Pie data={data.health_distribution} dataKey="value" nameKey="name" innerRadius={48} outerRadius={72} paddingAngle={3}>
                    {data.health_distribution.map((d) => (
                    <Cell key={d.key} fill={COLORS[d.key] ?? '#3154ff'} />
                    ))}
                  </Pie>
                  <Tooltip contentStyle={tooltipStyle} />
                </PieChart>
              </ResponsiveContainer>
            </div>
            <ul className="space-y-2 text-sm">
              {data.health_distribution.map((d) => (
                <li key={d.key} className="flex items-center gap-2">
                  <span className="h-2 w-2 rounded-full" style={{ background: COLORS[d.key] }} />
                  <span className="text-parchment-200/70">{d.name}</span>
                  <span className="ml-auto tabular-nums">{d.value}</span>
                </li>
              ))}
            </ul>
          </div>
        </Card>

        <Card className="lg:col-span-3">
          <CardHeader eyebrow="Temporal" title="Risk trend" />
          <div className="h-56 p-3">
            <ResponsiveContainer>
              <AreaChart data={data.risk_trend}>
                <defs>
                  <linearGradient id="crit" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#e06b6b" stopOpacity={0.45} />
                    <stop offset="100%" stopColor="#e06b6b" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid stroke="rgba(49,84,255,0.1)" vertical={false} />
                <XAxis dataKey="month" tick={{ fill: '#637097', fontSize: 11 }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fill: '#637097', fontSize: 11 }} axisLine={false} tickLine={false} />
                <Tooltip contentStyle={tooltipStyle} />
                <Area type="monotone" dataKey="critical" stroke="#e06b6b" fill="url(#crit)" strokeWidth={2} />
                <Area type="monotone" dataKey="at_risk" stroke="#fb923c" fill="transparent" strokeWidth={2} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </Card>
      </div>

      <div className="mt-4 grid gap-4 lg:grid-cols-2">
        <Card>
          <CardHeader eyebrow="Efficiency" title="Cost vs progress" />
          <div className="h-64 p-3">
            <ResponsiveContainer>
              <ScatterChart>
                <CartesianGrid stroke="rgba(49,84,255,0.1)" />
                <XAxis dataKey="progress" name="Progress" unit="%" tick={{ fill: '#637097', fontSize: 11 }} />
                <YAxis dataKey="expenditure_pct" name="Spend" unit="%" tick={{ fill: '#637097', fontSize: 11 }} />
                <ZAxis dataKey="risk" range={[40, 180]} />
                <Tooltip contentStyle={tooltipStyle} />
                <Scatter data={data.cost_vs_progress}>
                  {data.cost_vs_progress.map((d, i) => (
                    <Cell key={i} fill={COLORS[String(d.health)] ?? '#3154ff'} />
                  ))}
                </Scatter>
              </ScatterChart>
            </ResponsiveContainer>
          </div>
        </Card>

        <Card>
          <CardHeader
            eyebrow="Alerts"
            title="Priority interventions"
            action={
              <Link to="/app/risks" className="text-xs text-parchment-300 hover:underline">
                Open monitor
              </Link>
            }
          />
          <ul className="divide-y divide-[#e5ebff]">
            {data.recent_alerts.map((a) => (
              <li key={a.project_id} className="px-5 py-3">
                <Link to={`/app/projects/${a.project_id}`} className="block hover:text-parchment-100">
                  <div className="flex items-center justify-between gap-3">
                    <p className="truncate text-sm">{a.project_name}</p>
                    <HealthBadge status={a.health_status} />
                  </div>
                  <p className="mt-1 truncate text-xs text-parchment-200/50">{a.message}</p>
                </Link>
              </li>
            ))}
          </ul>
        </Card>
      </div>

      <Card className="mt-4 overflow-hidden">
        <CardHeader eyebrow="Watchlist" title="Critical projects" />
        <div className="overflow-x-auto">
          <table className="min-w-full text-left text-sm">
            <thead className="bg-parchment-300/5 font-mono text-[10px] uppercase tracking-[0.16em] text-parchment-200/70">
              <tr>
                <th className="px-5 py-3">Project</th>
                <th className="px-5 py-3">State</th>
                <th className="px-5 py-3">Agency</th>
                <th className="px-5 py-3">Progress</th>
                <th className="px-5 py-3">Risk</th>
                <th className="px-5 py-3">Status</th>
                <th className="px-5 py-3"></th>
              </tr>
            </thead>
            <tbody>
              {data.critical_projects.map((p) => (
                <tr key={p.id} className="border-t border-[#e5ebff] hover:bg-parchment-300/5">
                  <td className="px-5 py-3 font-medium">{p.project_name}</td>
                  <td className="px-5 py-3 text-parchment-200/60">{p.state}</td>
                  <td className="px-5 py-3 text-parchment-200/60">{p.agency}</td>
                  <td className="px-5 py-3 tabular-nums">{pct(p.physical_progress_pct)}</td>
                  <td className="px-5 py-3 tabular-nums" style={{ color: healthTone(p.health_status).fill }}>
                    {p.overall_risk_score}
                  </td>
                  <td className="px-5 py-3">
                    <HealthBadge status={p.health_status} />
                  </td>
                  <td className="px-5 py-3">
                    <Link to={`/app/projects/${p.id}`} className="text-xs text-parchment-300 hover:underline">
                      Open
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  )
}

const tooltipStyle = {
  background: '#ffffff',
  border: '1px solid rgba(49,84,255,0.14)',
  borderRadius: 12,
  fontSize: 12,
  color: '#16204a',
}
