import { healthTone } from '../../lib/utils'

export function HealthRing({
  score,
  size = 176,
  label,
}: {
  score: number
  size?: number
  label?: string
}) {
  const t = healthTone(
    score <= 30 ? 'HEALTHY' : score <= 50 ? 'WATCH' : score <= 70 ? 'AT_RISK' : 'CRITICAL',
  )
  const stroke = 10
  const r = (size - stroke) / 2
  const c = 2 * Math.PI * r
  const offset = c - (Math.min(score, 100) / 100) * c
  return (
    <div className="relative inline-flex items-center justify-center" style={{ width: size, height: size }}>
      <svg width={size} height={size} className="-rotate-90">
        <circle cx={size / 2} cy={size / 2} r={r} stroke="rgba(255,255,255,0.06)" strokeWidth={stroke} fill="none" />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={r}
          stroke={t.fill}
          strokeWidth={stroke}
          fill="none"
          strokeLinecap="round"
          strokeDasharray={c}
          strokeDashoffset={offset}
          style={{ transition: 'stroke-dashoffset 1.1s cubic-bezier(.22,1,.36,1)' }}
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="font-display text-4xl font-semibold tabular-nums">{Math.round(score)}</span>
        <span className="font-mono text-[10px] uppercase tracking-[0.2em] text-parchment-200/60">
          {label ?? '/ 100'}
        </span>
      </div>
    </div>
  )
}
