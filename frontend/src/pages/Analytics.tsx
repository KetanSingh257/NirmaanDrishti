import { useQuery } from '@tanstack/react-query'
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Scatter,
  ScatterChart,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import { fetchAnalytics } from '../lib/api'
import { Card, CardHeader } from '../components/ui/Card'
import { ErrorState, LoadingState } from '../components/ui/States'
import { PageHeader } from '../components/shared/PageHeader'

const COLORS: Record<string, string> = {
  HEALTHY: '#4aa87a',
  WATCH: '#d4a017',
  AT_RISK: '#fb923c',
  CRITICAL: '#e06b6b',
}

export default function Analytics() {
  const { data, isLoading, isError } = useQuery({ queryKey: ['analytics'], queryFn: fetchAnalytics })
  if (isLoading) return <LoadingState label="Compiling portfolio analytics…" />
  if (isError || !data) return <ErrorState />

  return (
    <div>
      <PageHeader
        eyebrow="Portfolio"
        title="Analytics"
        subtitle="State, agency and sector performance derived from live engine scores."
      />

      <div className="grid gap-4 lg:grid-cols-2">
        <Card>
          <CardHeader eyebrow="Geography" title="State-wise risk" />
          <div className="h-72 p-3">
            <ResponsiveContainer>
              <BarChart data={data.state_risk} layout="vertical" margin={{ left: 24 }}>
                <CartesianGrid stroke="rgba(255,255,255,0.04)" horizontal={false} />
                <XAxis type="number" tick={{ fill: '#8d8778', fontSize: 11 }} />
                <YAxis type="category" dataKey="state" width={110} tick={{ fill: '#cfc6b0', fontSize: 11 }} />
                <Tooltip contentStyle={tooltipStyle} labelStyle={tooltipLabelStyle} itemStyle={tooltipItemStyle} />
                <Bar dataKey="avg_risk" fill="#c4a35a" radius={[0, 6, 6, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Card>

        <Card>
          <CardHeader eyebrow="Implementing agency" title="Agency performance" />
          <div className="h-72 p-3">
            <ResponsiveContainer>
              <BarChart data={data.agency_performance}>
                <CartesianGrid stroke="rgba(255,255,255,0.04)" vertical={false} />
                <XAxis dataKey="agency" hide />
                <YAxis tick={{ fill: '#8d8778', fontSize: 11 }} />
                <Tooltip contentStyle={tooltipStyle} labelStyle={tooltipLabelStyle} itemStyle={tooltipItemStyle} />
                <Bar dataKey="avg_progress" fill="#6ec8c0" radius={[6, 6, 0, 0]} />
                <Bar dataKey="avg_risk" fill="#e06b6b" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Card>

        <Card>
          <CardHeader eyebrow="Money" title="Largest predicted overruns" />
          <div className="h-72 p-3">
            <ResponsiveContainer>
              <BarChart data={data.cost_overruns}>
                <CartesianGrid stroke="rgba(255,255,255,0.04)" vertical={false} />
                <XAxis dataKey="name" hide />
                <YAxis tick={{ fill: '#8d8778', fontSize: 11 }} />
                <Tooltip contentStyle={tooltipStyle} labelStyle={tooltipLabelStyle} itemStyle={tooltipItemStyle} />
                <Bar dataKey="overrun_cr" fill="#fb923c" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Card>

        <Card>
          <CardHeader eyebrow="Schedule" title="Delay distribution" />
          <div className="h-72 p-3">
            <ResponsiveContainer>
              <BarChart data={data.delay_distribution}>
                <CartesianGrid stroke="rgba(255,255,255,0.04)" vertical={false} />
                <XAxis dataKey="bucket" tick={{ fill: '#8d8778', fontSize: 11 }} />
                <YAxis tick={{ fill: '#8d8778', fontSize: 11 }} />
                <Tooltip contentStyle={tooltipStyle} labelStyle={tooltipLabelStyle} itemStyle={tooltipItemStyle} />
                <Bar dataKey="count" fill="#c4a35a" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Card>

        <Card>
          <CardHeader eyebrow="Health" title="Portfolio mix" />
          <div className="h-64 p-3">
            <ResponsiveContainer>
              <PieChart>
                <Pie data={data.health_distribution} dataKey="value" nameKey="name" innerRadius={50} outerRadius={80}>
                  {data.health_distribution.map((d) => (
                    <Cell key={d.key} fill={COLORS[d.key] ?? '#c4a35a'} />
                  ))}
                </Pie>
                <Tooltip contentStyle={tooltipStyle} labelStyle={tooltipLabelStyle} itemStyle={tooltipItemStyle} />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </Card>

        <Card>
          <CardHeader eyebrow="Temporal" title="Risk & overrun trend" />
          <div className="h-64 p-3">
            <ResponsiveContainer>
              <LineChart data={data.risk_trends}>
                <CartesianGrid stroke="rgba(255,255,255,0.04)" />
                <XAxis dataKey="month" tick={{ fill: '#8d8778', fontSize: 11 }} />
                <YAxis tick={{ fill: '#8d8778', fontSize: 11 }} />
                <Tooltip contentStyle={tooltipStyle} labelStyle={tooltipLabelStyle} itemStyle={tooltipItemStyle} />
                <Line type="monotone" dataKey="avg_risk" stroke="#e06b6b" strokeWidth={2} dot={false} />
                <Line type="monotone" dataKey="overrun_cr" stroke="#c4a35a" strokeWidth={2} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </Card>

        <Card className="lg:col-span-2">
          <CardHeader eyebrow="Efficiency" title="Progress vs expenditure" />
          <div className="h-72 p-3">
            <ResponsiveContainer>
              <ScatterChart>
                <CartesianGrid stroke="rgba(255,255,255,0.04)" />
                <XAxis dataKey="progress" name="Progress" unit="%" tick={{ fill: '#8d8778', fontSize: 11 }} />
                <YAxis dataKey="spend_pct" name="Spend" unit="%" tick={{ fill: '#8d8778', fontSize: 11 }} />
                <Tooltip contentStyle={tooltipStyle} labelStyle={tooltipLabelStyle} itemStyle={tooltipItemStyle} />
                <Scatter data={data.progress_vs_expenditure}>
                  {data.progress_vs_expenditure.map((d, i) => (
                    <Cell key={i} fill={COLORS[String(d.health)] ?? '#c4a35a'} />
                  ))}
                </Scatter>
              </ScatterChart>
            </ResponsiveContainer>
          </div>
        </Card>
      </div>
    </div>
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
