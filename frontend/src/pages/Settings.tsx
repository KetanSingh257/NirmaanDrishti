import { useQuery } from '@tanstack/react-query'
import { fetchHealth } from '../lib/api'
import { Card, CardHeader } from '../components/ui/Card'
import { PageHeader } from '../components/shared/PageHeader'

export default function Settings() {
  const health = useQuery({ queryKey: ['health'], queryFn: fetchHealth })

  return (
    <div>
      <PageHeader
        eyebrow="Platform"
        title="Settings"
        subtitle="Runtime configuration. Model artifacts are hot-swappable without a frontend change."
      />
      <div className="grid gap-4 lg:grid-cols-2">
        <Card>
          <CardHeader eyebrow="API" title="Service health" />
          <div className="space-y-3 p-5 text-sm">
            <Row k="Status" v={health.data?.status ?? (health.isError ? 'unreachable' : 'checking…')} />
            <Row k="Service" v={health.data?.service ?? '—'} />
            <Row k="Version" v={health.data?.version ?? '—'} />
            <Row k="Client proxy" v="/api → FastAPI :8000" />
          </div>
        </Card>
        <Card>
          <CardHeader eyebrow="Intelligence layer" title="Fusion weights" />
          <div className="space-y-3 p-5 text-sm">
            <Row k="Cost risk" v="40%" />
            <Row k="Time risk" v="35%" />
            <Row k="Trend risk" v="25%" />
            <Row k="Healthy" v="0 – 30" />
            <Row k="Watch" v="31 – 50" />
            <Row k="At risk" v="51 – 70" />
            <Row k="Critical" v="71 – 100" />
          </div>
        </Card>
        <Card className="lg:col-span-2">
          <CardHeader eyebrow="ML" title="Model integration" />
          <div className="space-y-2 p-5 text-sm leading-relaxed text-parchment-200/70">
            <p>
              Place <code className="text-parchment-100">model.pkl</code>,{' '}
              <code className="text-parchment-100">preprocessor.pkl</code> and{' '}
              <code className="text-parchment-100">feature_config.json</code> in{' '}
              <code className="text-parchment-100">backend/app/ml/cost/artifacts/</code>.
            </p>
            <p>
              Restart FastAPI. The cost engine loads artifacts automatically and the API contract
              stays identical — this UI does not need to change.
            </p>
          </div>
        </Card>
      </div>
    </div>
  )
}

function Row({ k, v }: { k: string; v: string }) {
  return (
    <div className="flex items-center justify-between border-b border-[#e5ebff] py-2 last:border-0">
      <span className="text-parchment-200/50">{k}</span>
      <span className="tabular-nums">{v}</span>
    </div>
  )
}
