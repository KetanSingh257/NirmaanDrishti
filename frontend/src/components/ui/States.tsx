import { AlertTriangle, Inbox, Loader2 } from 'lucide-react'

export function LoadingState({ label = 'Assembling intelligence…' }: { label?: string }) {
  return (
    <div className="flex min-h-[240px] flex-col items-center justify-center gap-3 text-parchment-200/70">
      <Loader2 className="h-6 w-6 animate-spin text-parchment-300" />
      <p className="font-mono text-xs uppercase tracking-[0.2em]">{label}</p>
    </div>
  )
}

export function ErrorState({ message }: { message?: string }) {
  return (
    <div className="flex min-h-[240px] flex-col items-center justify-center gap-3 text-signal-rose">
      <AlertTriangle className="h-6 w-6" />
      <p className="text-sm">{message ?? 'Unable to reach the intelligence service.'}</p>
    </div>
  )
}

export function EmptyState({ message }: { message: string }) {
  return (
    <div className="flex min-h-[200px] flex-col items-center justify-center gap-3 text-parchment-200/60">
      <Inbox className="h-6 w-6" />
      <p className="text-sm">{message}</p>
    </div>
  )
}
