import { cn } from '../../lib/utils'
import { healthTone, riskTone, trendTone } from '../../lib/utils'

export function Badge({
  children,
  className,
}: {
  children: React.ReactNode
  className?: string
}) {
  return (
    <span
      className={cn(
        'inline-flex items-center gap-1 rounded-full border px-2 py-0.5 text-[10px] font-medium uppercase tracking-[0.14em]',
        className,
      )}
    >
      {children}
    </span>
  )
}

export function HealthBadge({ status }: { status?: string }) {
  const t = healthTone(status)
  return <Badge className={cn(t.bg, t.border, t.text)}>{t.label}</Badge>
}

export function RiskBadge({ level }: { level?: string }) {
  const t = riskTone(level)
  return <Badge className={cn(t.bg, t.border, t.text)}>{level ?? '—'}</Badge>
}

export function TrendBadge({ trend }: { trend?: string }) {
  const t = trendTone(trend)
  return <Badge className={cn(t.bg, t.border, t.text)}>{(trend ?? '—').replace('_', ' ')}</Badge>
}
