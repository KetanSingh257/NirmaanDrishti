import { Link, useParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { Clock3, TrendingDown, Wallet } from 'lucide-react'
import { fetchIntelligence, fetchProject } from '../lib/api'
import { daysLabel, inrCr, pct, prettyDate, signedPct } from '../lib/format'
import { healthTone } from '../lib/utils'
import { Card } from '../components/ui/Card'
import { HealthBadge, RiskBadge, TrendBadge } from '../components/ui/Badge'
import { ErrorState, LoadingState } from '../components/ui/States'
import { HealthRing } from '../components/shared/HealthRing'
import { PageHeader } from '../components/shared/PageHeader'

export default function ProjectDetail() {
  const { id } = useParams()
  const project = useQuery({ queryKey: ['project', id], queryFn: () => fetchProject(id!) })
  const intel = useQuery({ queryKey: ['intel', id], queryFn: () => fetchIntelligence(id!) })

  if (project.isLoading || intel.isLoading) return <LoadingState label="Opening dossier…" />
  if (project.isError || intel.isError || !project.data || !intel.data) return <ErrorState />

  const p = project.data
  const i = intel.data
  const tone = healthTone(i.health_status)

  return (
    <div>
      <PageHeader
        eyebrow={p.project_code}
        title={p.project_name}
        subtitle={`${p.location ?? p.state} · ${p.agency} · ${p.sector}`}
        actions={<HealthBadge status={i.health_status} />}
      />

      <div className="mb-4 flex flex-wrap gap-3 text-xs text-parchment-200/55">
        <span>State · {p.state}</span>
        <span>Agency · {p.agency}</span>
        <span>ID · {p.id}</span>
        <span>Status · {p.status}</span>
      </div>

      <div className="grid gap-4 md:grid-cols-3 xl:grid-cols-6">
        <Metric label="Original cost" value={inrCr(p.original_cost_cr)} />
        <Metric label="Revised cost" value={inrCr(p.revised_cost_cr)} />
        <Metric label="Expenditure" value={inrCr(p.current_expenditure_cr)} />
        <Metric label="Physical progress" value={pct(p.physical_progress_pct)} />
        <Metric label="Project age" value={daysLabel(p.project_age_days)} />
        <Metric label="Days overdue" value={daysLabel(p.days_overdue)} />
      </div>

      <div className="mt-4 grid gap-4 lg:grid-cols-5">
        <Card className="flex flex-col items-center justify-center p-8 lg:col-span-2">
          <p className="mb-4 font-mono text-[10px] uppercase tracking-[0.24em] text-parchment-300/70">
            Project health
          </p>
          <HealthRing score={i.overall_risk_score} />
          <p className={`mt-4 font-display text-xl ${tone.text}`}>{tone.label}</p>
          <p className="mt-1 text-center text-xs text-parchment-200/50">
            Weighted fusion · cost 40% · time 35% · trend 25%
          </p>
        </Card>
        <Card className="p-6 lg:col-span-3">
          <p className="font-mono text-[10px] uppercase tracking-[0.22em] text-parchment-300/70">Key insights</p>
          <ul className="mt-4 space-y-3">
            {i.key_insights.map((n) => (
              <li key={n} className="flex gap-3 text-sm text-parchment-100/80">
                <span className="mt-1 h-1.5 w-1.5 shrink-0 rounded-full bg-parchment-300" />
                {n}
              </li>
            ))}
          </ul>
          {p.description && <p className="mt-6 text-sm leading-relaxed text-parchment-200/55">{p.description}</p>}
        </Card>
      </div>

      <div className="mt-4 grid gap-4 lg:grid-cols-3">
        <Link to="/app/intelligence/cost" className="block">
          <Card className="h-full p-6 transition hover:border-parchment-300/30">
            <div className="mb-4 flex items-center gap-2 text-parchment-300">
              <Wallet className="h-4 w-4" />
              <p className="font-mono text-[10px] uppercase tracking-[0.2em]">Cost intelligence</p>
            </div>
            <p className="text-xs text-parchment-200/45">Predicted expenditure</p>
            <p className="font-display text-2xl">{inrCr(i.cost.predicted_expenditure_cr)}</p>
            <p className="mt-3 text-xs text-parchment-200/45">Potential overrun</p>
            <p className="text-lg text-signal-rose">{inrCr(i.cost.predicted_overrun_cr)}</p>
            <div className="mt-4">
              <RiskBadge level={i.cost.risk_level} />
            </div>
          </Card>
        </Link>
        <Link to="/app/intelligence/time" className="block">
          <Card className="h-full p-6 transition hover:border-parchment-300/30">
            <div className="mb-4 flex items-center gap-2 text-parchment-300">
              <Clock3 className="h-4 w-4" />
              <p className="font-mono text-[10px] uppercase tracking-[0.2em]">Time intelligence</p>
            </div>
            <p className="text-xs text-parchment-200/45">Predicted delay</p>
            <p className="font-display text-2xl">{i.time.predicted_delay_days} days</p>
            <p className="mt-3 text-xs text-parchment-200/45">Estimated completion</p>
            <p className="text-lg">{prettyDate(i.time.estimated_completion_date)}</p>
            <div className="mt-4">
              <RiskBadge level={i.time.risk_level} />
            </div>
          </Card>
        </Link>
        <Link to={`/app/intelligence/trend?project=${p.id}`} className="block">
          <Card className="h-full p-6 transition hover:border-parchment-300/30">
            <div className="mb-4 flex items-center gap-2 text-parchment-300">
              <TrendingDown className="h-4 w-4" />
              <p className="font-mono text-[10px] uppercase tracking-[0.2em]">Trend intelligence</p>
            </div>
            <p className="text-xs text-parchment-200/45">Trend</p>
            <p className="font-display text-2xl">{i.trend.trend.replace('_', ' ')}</p>
            <p className="mt-3 text-xs text-parchment-200/45">Progress velocity</p>
            <p className="text-lg">{signedPct(i.trend.progress_velocity)}</p>
            <p className="text-xs text-parchment-200/45">Expenditure growth {signedPct(i.trend.expenditure_velocity)}</p>
            <div className="mt-4">
              <TrendBadge trend={i.trend.trend} />
            </div>
          </Card>
        </Link>
      </div>
    </div>
  )
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="glass rounded-xl p-4">
      <p className="font-mono text-[9px] uppercase tracking-[0.16em] text-parchment-200/70">{label}</p>
      <p className="mt-1 text-sm font-medium tabular-nums">{value}</p>
    </div>
  )
}
