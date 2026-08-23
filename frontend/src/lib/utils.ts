import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function healthTone(status?: string) {
  switch (status) {
    case 'HEALTHY':
      return {
        text: 'text-signal-emerald',
        bg: 'bg-signal-emerald/10',
        border: 'border-signal-emerald/30',
        fill: '#4aa87a',
        label: 'Healthy',
      }
    case 'WATCH':
      return {
        text: 'text-signal-amber',
        bg: 'bg-signal-amber/10',
        border: 'border-signal-amber/30',
        fill: '#d4a017',
        label: 'Watch',
      }
    case 'AT_RISK':
      return {
        text: 'text-orange-400',
        bg: 'bg-orange-400/10',
        border: 'border-orange-400/30',
        fill: '#fb923c',
        label: 'At Risk',
      }
    case 'CRITICAL':
      return {
        text: 'text-signal-rose',
        bg: 'bg-signal-rose/10',
        border: 'border-signal-rose/30',
        fill: '#e06b6b',
        label: 'Critical',
      }
    default:
      return {
        text: 'text-parchment-200',
        bg: 'bg-parchment-300/5',
        border: 'border-parchment-300/15',
        fill: '#3154ff',
        label: status ?? '—',
      }
  }
}

export function riskTone(level?: string) {
  switch (level) {
    case 'LOW':
      return healthTone('HEALTHY')
    case 'MEDIUM':
      return healthTone('WATCH')
    case 'HIGH':
      return healthTone('AT_RISK')
    case 'CRITICAL':
      return healthTone('CRITICAL')
    default:
      return healthTone()
  }
}

export function trendTone(trend?: string) {
  if (trend === 'IMPROVING') return healthTone('HEALTHY')
  if (trend === 'STABLE') return healthTone('WATCH')
  if (trend === 'WEAKENING') return healthTone('AT_RISK')
  if (trend === 'DETERIORATING') return healthTone('CRITICAL')
  return healthTone()
}
