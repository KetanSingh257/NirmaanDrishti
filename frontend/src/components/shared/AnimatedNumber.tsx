import { useEffect, useState } from 'react'

export function AnimatedNumber({
  value,
  duration = 900,
  format,
}: {
  value: number
  duration?: number
  format?: (n: number) => string
}) {
  const [shown, setShown] = useState(0)
  useEffect(() => {
    const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches
    if (reduce) {
      setShown(value)
      return
    }
    let frame: number
    const start = performance.now()
    const from = 0
    const tick = (now: number) => {
      const t = Math.min(1, (now - start) / duration)
      const eased = 1 - Math.pow(1 - t, 3)
      setShown(from + (value - from) * eased)
      if (t < 1) frame = requestAnimationFrame(tick)
    }
    frame = requestAnimationFrame(tick)
    return () => cancelAnimationFrame(frame)
  }, [value, duration])
  return <>{format ? format(shown) : Math.round(shown).toLocaleString('en-IN')}</>
}
