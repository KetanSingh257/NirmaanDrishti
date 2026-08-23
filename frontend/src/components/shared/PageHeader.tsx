export function PageHeader({
  eyebrow,
  title,
  subtitle,
  actions,
}: {
  eyebrow?: string
  title: string
  subtitle?: string
  actions?: React.ReactNode
}) {
  return (
    <div className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
      <div>
        {eyebrow && (
          <p className="mb-1 font-mono text-[10px] uppercase tracking-[0.24em] text-parchment-300/70">
            {eyebrow}
          </p>
        )}
        <h1 className="font-display text-2xl font-semibold tracking-tight text-parchment-50 sm:text-3xl">
          {title}
        </h1>
        {subtitle && <p className="mt-1 max-w-2xl text-sm text-parchment-200/60">{subtitle}</p>}
      </div>
      {actions}
    </div>
  )
}
