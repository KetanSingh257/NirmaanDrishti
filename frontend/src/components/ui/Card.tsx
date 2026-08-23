import { cn } from '../../lib/utils'

export function Card({
  className,
  children,
}: {
  className?: string
  children: React.ReactNode
}) {
  return (
    <div className={cn('glass rounded-lg shadow-card', className)}>{children}</div>
  )
}

export function CardHeader({
  eyebrow,
  title,
  action,
}: {
  eyebrow?: string
  title: string
  action?: React.ReactNode
}) {
  return (
    <div className="flex items-start justify-between gap-3 border-b border-[#e5ebff] bg-white/45 px-5 py-4">
      <div>
        {eyebrow && (
          <p className="mb-1 font-mono text-[10px] uppercase tracking-[0.22em] text-parchment-300/70">
            {eyebrow}
          </p>
        )}
        <h3 className="font-display text-base font-semibold tracking-tight text-parchment-50">
          {title}
        </h3>
      </div>
      {action}
    </div>
  )
}
