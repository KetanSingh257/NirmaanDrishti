import { useMemo, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { Search } from 'lucide-react'
import { fetchFilters, fetchProjects } from '../lib/api'
import { inrCr, pct } from '../lib/format'
import { HealthBadge, TrendBadge } from '../components/ui/Badge'
import { Card } from '../components/ui/Card'
import { Input, Select } from '../components/ui/Input'
import { ErrorState, LoadingState } from '../components/ui/States'
import { PageHeader } from '../components/shared/PageHeader'

export default function Projects() {
  const [search, setSearch] = useState('')
  const [state, setState] = useState('')
  const [agency, setAgency] = useState('')
  const [risk, setRisk] = useState('')
  const [status, setStatus] = useState('')
  const [sort, setSort] = useState('risk_desc')
  const [page, setPage] = useState(1)

  const filters = useQuery({ queryKey: ['filters'], queryFn: fetchFilters })
  const params = useMemo(
    () => ({
      page,
      limit: 12,
      search: search || undefined,
      state: state || undefined,
      agency: agency || undefined,
      risk_level: risk || undefined,
      status: status || undefined,
      sort,
    }),
    [page, search, state, agency, risk, status, sort],
  )
  const list = useQuery({ queryKey: ['projects', params], queryFn: () => fetchProjects(params) })

  return (
    <div>
      <PageHeader
        eyebrow="Explorer"
        title="Infrastructure portfolio"
        subtitle="Search and filter the monitored programme. Click any row for the full intelligence dossier."
      />

      <Card className="mb-5 p-4">
        <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-6">
          <div className="relative xl:col-span-2">
            <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-parchment-200/60" />
            <Input
              className="pl-9"
              placeholder="Search name, code, agency…"
              value={search}
              onChange={(e) => {
                setSearch(e.target.value)
                setPage(1)
              }}
            />
          </div>
          <Select value={state} onChange={(e) => { setState(e.target.value); setPage(1) }}>
            <option value="">All states</option>
            {filters.data?.states.map((s) => <option key={s}>{s}</option>)}
          </Select>
          <Select value={agency} onChange={(e) => { setAgency(e.target.value); setPage(1) }}>
            <option value="">All agencies</option>
            {filters.data?.agencies.map((s) => <option key={s}>{s}</option>)}
          </Select>
          <Select value={risk} onChange={(e) => { setRisk(e.target.value); setPage(1) }}>
            <option value="">All health</option>
            {filters.data?.risk_levels.map((s) => <option key={s} value={s}>{s.replace('_', ' ')}</option>)}
          </Select>
          <Select value={sort} onChange={(e) => setSort(e.target.value)}>
            <option value="risk_desc">Risk: high → low</option>
            <option value="risk_asc">Risk: low → high</option>
            <option value="expenditure_desc">Expenditure</option>
            <option value="progress_asc">Progress: lagging</option>
            <option value="progress_desc">Progress: advanced</option>
            <option value="name">Name</option>
          </Select>
        </div>
        <div className="mt-3 flex gap-3">
          <Select value={status} onChange={(e) => { setStatus(e.target.value); setPage(1) }} className="max-w-xs">
            <option value="">All statuses</option>
            {filters.data?.statuses.map((s) => <option key={s}>{s}</option>)}
          </Select>
        </div>
      </Card>

      {list.isLoading ? (
        <LoadingState />
      ) : list.isError || !list.data ? (
        <ErrorState />
      ) : (
        <>
          <div className="mb-3 font-mono text-[10px] uppercase tracking-[0.18em] text-parchment-200/45">
            {list.data.total} projects
          </div>
          <div className="grid gap-4 md:grid-cols-2">
            {list.data.items.map((p) => (
              <Link key={p.id} to={`/app/projects/${p.id}`} className="glass rounded-xl p-5 transition hover:border-parchment-300/30">
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <p className="font-mono text-[10px] uppercase tracking-[0.16em] text-parchment-300/70">
                      {p.project_code}
                    </p>
                    <h3 className="mt-1 font-display text-lg leading-snug">{p.project_name}</h3>
                    <p className="mt-1 text-xs text-parchment-200/50">
                      {p.state} · {p.agency} · {p.sector}
                    </p>
                  </div>
                  <HealthBadge status={p.health_status} />
                </div>
                <div className="mt-4 grid grid-cols-3 gap-3 text-sm">
                  <Stat label="Progress" value={pct(p.physical_progress_pct)} />
                  <Stat label="Spend" value={inrCr(p.current_expenditure_cr)} />
                  <Stat label="Risk" value={String(p.overall_risk_score)} />
                </div>
                <div className="mt-3">
                  <TrendBadge trend={p.trend} />
                </div>
              </Link>
            ))}
          </div>
          <div className="mt-6 flex items-center justify-between text-sm text-parchment-200/60">
            <button disabled={page <= 1} onClick={() => setPage((p) => p - 1)} className="disabled:opacity-30">
              Previous
            </button>
            <span>
              Page {list.data.page} / {list.data.pages}
            </span>
            <button
              disabled={page >= list.data.pages}
              onClick={() => setPage((p) => p + 1)}
              className="disabled:opacity-30"
            >
              Next
            </button>
          </div>
        </>
      )}
    </div>
  )
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <p className="font-mono text-[9px] uppercase tracking-[0.16em] text-parchment-200/70">{label}</p>
      <p className="tabular-nums">{value}</p>
    </div>
  )
}
