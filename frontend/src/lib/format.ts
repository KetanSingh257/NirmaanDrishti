export function inrCr(value?: number | null, digits = 0) {
  if (value === undefined || value === null || Number.isNaN(value)) return '—'
  return `₹${value.toLocaleString('en-IN', {
    maximumFractionDigits: digits,
    minimumFractionDigits: digits,
  })} Cr`
}

export function compactInr(value?: number | null) {
  if (value === undefined || value === null) return '—'
  if (Math.abs(value) >= 100000) return `₹${(value / 100000).toFixed(2)} L Cr`
  if (Math.abs(value) >= 1000) return `₹${(value / 1000).toFixed(2)}k Cr`
  return inrCr(value, value < 100 ? 1 : 0)
}

export function pct(value?: number | null, digits = 1) {
  if (value === undefined || value === null) return '—'
  return `${value.toFixed(digits)}%`
}

export function daysLabel(n?: number | null) {
  if (n === undefined || n === null) return '—'
  return `${n.toLocaleString('en-IN')} days`
}

export function prettyDate(value?: string | null) {
  if (!value) return '—'
  const d = new Date(value)
  if (Number.isNaN(d.getTime())) return value
  return d.toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' })
}

export function signedPct(value?: number | null) {
  if (value === undefined || value === null) return '—'
  const sign = value > 0 ? '+' : ''
  return `${sign}${value.toFixed(1)}%`
}
