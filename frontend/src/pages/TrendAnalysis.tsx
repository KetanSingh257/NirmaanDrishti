import { useEffect, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { useSearchParams } from 'react-router-dom'
import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import { analyzeTrend, fetchProjectOptions } from '../lib/api'
import { signedPct } from '../lib/format'
import { trendTone } from '../lib/utils'
import { Card, CardHeader } from '../components/ui/Card'
import { ErrorState, LoadingState } from '../components/ui/States'
import { PageHeader } from '../components/shared/PageHeader'
import { ProjectPicker } from '../components/shared/ProjectPicker'

export default function TrendAnalysis() {
  const [params] = useSearchParams()
  const [projectId, setProjectId] = useState(params.get('project') ?? '')
  const list = useQuery({
    queryKey: ['projects-mini'],
    queryFn: fetchProjectOptions,
  })

  useEffect(() => {
    if (!projectId && list.data?.[0]) setProjectId(String(list.data[0].id))
  }, [list.data, projectId])

  const trend = useQuery({
    queryKey: ['trend', projectId],
    queryFn: () => analyzeTrend(projectId),
    enabled: Boolean(projectId),
  })

  const t = trend.data
  const tone = trendTone(t?.trend)

  return (
    <div>
      <PageHeader
        eyebrow="Engine 03"
        title="Trend intelligence"
        subtitle="Real velocity math on official progress updates — not a random mock."
      />
      <Card className="relative z-30 mb-5 max-w-xl overflow-visible p-4">
        <ProjectPicker label="Select project" projects={list.data ?? []} selected={projectId} onSelect={setProjectId} />
      </Card>

      {trend.isLoading ? (
        <LoadingState label="Computing velocities…" />
      ) : trend.isError || !t ? (
        <ErrorState />
      ) : (
        <>
          <div className="grid gap-4 lg:grid-cols-3">
            <Card className="flex flex-col items-center justify-center p-8 lg:col-span-1">
              <p className="font-mono text-[10px] uppercase tracking-[0.24em] text-parchment-300/70">Project trend</p>
              <p className={`mt-4 font-display text-3xl ${tone.text}`}>
                {t.trend === 'DETERIORATING' ? '↓' : t.trend === 'IMPROVING' ? '↑' : '→'} {t.trend.replace('_', ' ')}
              </p>
              <p className="mt-2 text-sm text-parchment-200/50">Score {t.trend_score} · {t.risk_level}</p>
            </Card>
            <div className="grid gap-3 sm:grid-cols-2 lg:col-span-2">
              <Stat label="Progress velocity" value={signedPct(t.progress_velocity)} />
              <Stat label="Expenditure growth" value={signedPct(t.expenditure_velocity)} />
              <Stat label="Cost efficiency" value={t.cost_efficiency.toFixed(2)} />
              <Stat label="Progress slowdown" value={signedPct(t.progress_slowdown)} />
            </div>
          </div>

          <Card className="mt-4">
            <CardHeader eyebrow="History" title="Progress vs expenditure" />
            <div className="h-72 p-3">
              <ResponsiveContainer>
                <LineChart data={t.series}>
                  <CartesianGrid stroke="rgba(255,255,255,0.05)" />
                  <XAxis dataKey="date" tick={{ fill: '#8d8778', fontSize: 11 }} />
                  <YAxis yAxisId="l" tick={{ fill: '#8d8778', fontSize: 11 }} />
                  <YAxis yAxisId="r" orientation="right" tick={{ fill: '#8d8778', fontSize: 11 }} />
                  <Tooltip contentStyle={tooltipStyle} labelStyle={tooltipLabelStyle} itemStyle={tooltipItemStyle} />
                  <Legend />
                  <Line yAxisId="l" type="monotone" dataKey="physical_progress_pct" name="Progress %" stroke="#c4a35a" strokeWidth={2} dot={false} />
                  <Line yAxisId="r" type="monotone" dataKey="expenditure_cr" name="Expenditure Cr" stroke="#6ec8c0" strokeWidth={2} dot={false} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </Card>

          <div className="mt-4 grid gap-3">
            {t.insights.map((n) => (
              <div key={n} className="glass rounded-xl px-4 py-3 text-sm">
                ⚠ {n}
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  )
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <Card className="p-5">
      <p className="font-mono text-[9px] uppercase tracking-[0.16em] text-parchment-200/70">{label}</p>
      <p className="mt-2 font-display text-2xl tabular-nums">{value}</p>
    </Card>
  )
}

const tooltipStyle = {
  background: '#111827',
  border: '1px solid rgba(255,255,255,0.14)',
  borderRadius: 12,
  color: '#f8fafc',
  fontSize: 12,
}

const tooltipLabelStyle = {
  color: '#ffffff',
  fontWeight: 700,
}

const tooltipItemStyle = {
  color: '#eaf0ff',
}
