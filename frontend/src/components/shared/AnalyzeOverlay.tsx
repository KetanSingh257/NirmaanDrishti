import { useEffect, useState } from 'react'
import { AnimatePresence, motion } from 'framer-motion'

export function AnalyzeOverlay({ active, steps }: { active: boolean; steps: string[] }) {
  const [i, setI] = useState(0)
  useEffect(() => {
    if (!active) {
      setI(0)
      return
    }
    const id = setInterval(() => setI((n) => (n + 1) % steps.length), 550)
    return () => clearInterval(id)
  }, [active, steps.length])

  return (
    <AnimatePresence>
      {active && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="absolute inset-0 z-10 flex flex-col items-center justify-center rounded-xl border border-parchment-300/20 bg-white/85 backdrop-blur-md"
        >
          <div className="mb-6 h-16 w-16 rounded-full border border-parchment-300/30">
            <div className="h-full w-full animate-spin rounded-full border-t border-parchment-300" />
          </div>
          <p className="font-mono text-[11px] uppercase tracking-[0.22em] text-parchment-300">
            {steps[i]}
          </p>
        </motion.div>
      )}
    </AnimatePresence>
  )
}
