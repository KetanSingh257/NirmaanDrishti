import { cn } from '../../lib/utils'

export function Field({
  label,
  children,
}: {
  label: string
  children: React.ReactNode
}) {
  return (
    <label className="block">
      <span className="mb-1.5 block font-mono text-[10px] uppercase tracking-[0.18em] text-parchment-200/55">
        {label}
      </span>
      {children}
    </label>
  )
}

export function Input(props: React.InputHTMLAttributes<HTMLInputElement>) {
  return (
    <input
      {...props}
      className={cn(
        'w-full rounded-lg border border-[#dfe6ff] bg-white px-3 py-2.5 text-sm text-parchment-50 outline-none transition placeholder:text-parchment-200/50 focus:border-parchment-300/60 focus:ring-4 focus:ring-parchment-300/10',
        props.className,
      )}
    />
  )
}

export function Select(props: React.SelectHTMLAttributes<HTMLSelectElement>) {
  return (
    <select
      {...props}
      className={cn(
        'w-full rounded-lg border border-[#dfe6ff] bg-white px-3 py-2.5 text-sm text-parchment-50 outline-none focus:border-parchment-300/60 focus:ring-4 focus:ring-parchment-300/10',
        props.className,
      )}
    />
  )
}
