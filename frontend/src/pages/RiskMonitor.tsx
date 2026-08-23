import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { fetchFilters, fetchRisks } from '../lib/api'
import { healthTone } from '../lib/utils'
import { Card } from '../components/ui/Card'
import { HealthBadge, RiskBadge, TrendBadge } from '../components/ui/Badge'
import { Select } from '../components/ui/Input'
import { ErrorState, LoadingState, EmptyState } from '../components/ui/States'
import { PageHeader } from '../components/shared/PageHeader'

export default function RiskMonitor() {
  const [focus, setFocus] = useState('')
  const [state, setState] = useState('')
  const [agency, setAgency] = useState('')
  const filters = useQuery({ queryKey: ['filters'], queryFn: fetchFilters })
  const risks = useQuery({
    queryKey: ['risks', focus, state, agency],
    queryFn: () => fetchRisks({ focus: focus || undefined, state: state || undefined, agency: agency || undefined }),
  })

  return (
    <div>
      <PageHeader
        eyebrow="Early warning"
        title="Risk monitor"
        subtitle="Command view of projects that require intervention — with the reasons the engines agree on."
      />

      <div className="mb-5 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <Select value={focus} onChange={(e) => setFocus(e.target.value)}>
          <option value="">All risk types</option>
          <option value="overall">Overall health</option>
          <option value="cost">Cost risk</option>
          <option value="time">Time risk</option>
          <option value="trend">Trend risk</option>
        </Select>
        <Select value={state} onChange={(e) => setState(e.target.value)}>
          <option value="">All states</option>
          {filters.data?.states.map((s) => <option key={s}>{s}</option>)}
        </Select>
        <Select value={agency} onChange={(e) => setAgency(e.target.value)}>
          <option value="">All agencies</option>
          {filters.data?.agencies.map((s) => <option key={s}>{s}</option>)}
        </Select>
        {risks.data && (
          <div className="flex items-center gap-4 font-mono text-[11px] uppercase tracking-[0.14em] text-parchment-200/55">
            <span className="text-signal-rose">{risks.data.critical_count} critical</span>
            <span className="text-orange-400">{risks.data.at_risk_count} at risk</span>
          </div>
        )}
      </div>

      {risks.isLoading ? (
        <LoadingState label="Scanning alerts…" />
      ) : risks.isError || !risks.data ? (
        <ErrorState />
      ) : risks.data.items.length === 0 ? (
        <EmptyState message="No projects match this risk filter." />
      ) : (
        <div className="grid gap-4 lg:grid-cols-2">
          {risks.data.items.map((r) => {
            const tone = healthTone(r.health_status)
            return (
              <Card key={r.project_id} className="p-5">
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <p className="font-mono text-[10px] uppercase tracking-[0.16em] text-parchment-300/70">
                      {r.project_code} · {r.state}
                    </p>
                    <h3 className="mt-1 font-display text-lg">{r.project_name}</h3>
                    <p className="text-xs text-parchment-200/50">{r.agency} · {r.sector}</p>
                  </div>
                  <HealthBadge status={r.health_status} />
                </div>
                <p className={`mt-4 font-display text-3xl ${tone.text}`}>{r.overall_risk_score}</p>
                <p className="font-mono text-[10px] uppercase tracking-[0.16em] text-parchment-200/70">Risk score</p>
                <div className="mt-3 flex flex-wrap gap-2">
                  <RiskBadge level={r.cost_risk_level} />
                  <RiskBadge level={r.time_risk_level} />
                  <TrendBadge trend={r.trend} />
                </div>
                <ul className="mt-4 space-y-1.5 text-sm text-parchment-100/75">
                  {r.reasons.map((reason) => (
                    <li key={reason}>• {reason}</li>
                  ))}
                </ul>
                <Link
                  to={`/app/projects/${r.project_id}`}
                  className="mt-4 inline-flex text-sm text-parchment-300 hover:underline"
                >
                  View project
                </Link>
              </Card>
            )
          })}
        </div>
      )}
    </div>
  )
}
