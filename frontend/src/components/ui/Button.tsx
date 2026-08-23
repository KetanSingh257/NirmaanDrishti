import { cn } from '../../lib/utils'
import type { ButtonHTMLAttributes } from 'react'

type Variant = 'primary' | 'ghost' | 'outline' | 'gold'

export function Button({
  className,
  variant = 'primary',
  ...props
}: ButtonHTMLAttributes<HTMLButtonElement> & { variant?: Variant }) {
  const styles: Record<Variant, string> = {
    primary:
      'bg-parchment-300 text-white hover:bg-parchment-400 shadow-glow border border-parchment-300',
    gold: 'bg-signal-amber text-parchment-50 hover:bg-[#ffc04d] shadow-card border border-signal-amber/40',
    outline:
      'border border-parchment-300/20 bg-white text-parchment-300 hover:border-parchment-300/50 hover:bg-parchment-300/5',
    ghost: 'text-parchment-200 hover:text-parchment-300 hover:bg-parchment-300/5',
  }
  return (
    <button
      className={cn(
        'inline-flex items-center justify-center gap-2 rounded-lg px-4 py-2 text-sm font-semibold transition disabled:opacity-50',
        styles[variant],
        className,
      )}
      {...props}
    />
  )
}
