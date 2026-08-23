import { useState } from 'react'
import { Outlet, useLocation } from 'react-router-dom'
import { Menu } from 'lucide-react'
import { motion } from 'framer-motion'
import Sidebar from './Sidebar'
import { cn } from '../../lib/utils'

const titles: Record<string, string> = {
  '/app/dashboard': 'Command Dashboard',
  '/app/projects': 'Project Explorer',
  '/app/intelligence/cost': 'Cost Intelligence',
  '/app/intelligence/time': 'Time Intelligence',
  '/app/intelligence/trend': 'Trend Intelligence',
  '/app/risks': 'Risk Monitor',
  '/app/analytics': 'Portfolio Analytics',
  '/app/settings': 'Platform Settings',
}

export default function AppLayout() {
  const [collapsed, setCollapsed] = useState(false)
  const [mobileOpen, setMobileOpen] = useState(false)
  const location = useLocation()
  const title =
    titles[location.pathname] ??
    (location.pathname.startsWith('/app/projects/') ? 'Project Dossier' : 'Sentinel')

  return (
    <div className="relative min-h-screen overflow-hidden bg-[#3154ff] text-parchment-50 grid-bg">
      <div className="pointer-events-none absolute inset-0">
        <div className="absolute -right-20 top-20 h-80 w-80 rounded-full border border-white/10" />
        <div className="absolute -right-6 top-32 h-56 w-56 rounded-full border border-white/10" />
        <div className="absolute left-10 top-24 hidden rounded-lg bg-white/90 px-6 py-3 font-display text-xl font-semibold text-parchment-50 shadow-card lg:block">
          300+ Screens
        </div>
        <div className="absolute right-24 top-24 hidden rounded-lg bg-white/90 px-6 py-3 font-display text-xl font-semibold text-parchment-50 shadow-card xl:block">
          100+ Components
        </div>
      </div>
      <Sidebar
        collapsed={collapsed}
        onToggle={() => setCollapsed((v) => !v)}
        mobileOpen={mobileOpen}
        onClose={() => setMobileOpen(false)}
      />
      <div
        className={cn(
          'relative min-h-screen transition-all duration-300 lg:py-8 lg:pr-8',
          collapsed ? 'lg:pl-[108px]' : 'lg:pl-[300px]',
        )}
      >
        <div className="min-h-screen overflow-hidden bg-[#f6f8ff] shadow-[0_42px_120px_-54px_rgba(10,24,120,0.9)] lg:min-h-[calc(100vh-4rem)] lg:rounded-[18px]">
        <header className="sticky top-0 z-20 flex h-16 items-center justify-between border-b border-[#e7ecff] bg-white/90 px-4 shadow-sm backdrop-blur-xl sm:px-6">
          <div className="flex items-center gap-3">
            <button
              className="rounded-lg border border-[#dfe6ff] bg-white p-2 text-parchment-300 shadow-sm lg:hidden"
              onClick={() => setMobileOpen(true)}
              aria-label="Open navigation"
            >
              <Menu className="h-4 w-4" />
            </button>
            <div>
              <p className="font-mono text-[10px] uppercase tracking-[0.2em] text-parchment-300/70">
                Live intelligence
              </p>
              <h2 className="font-display text-sm font-semibold">{title}</h2>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <span className="hidden items-center gap-2 rounded-full border border-signal-emerald/25 bg-signal-emerald/10 px-3 py-1 font-mono text-[10px] uppercase tracking-[0.16em] text-signal-emerald sm:inline-flex">
              <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-signal-emerald" />
              Engines online
            </span>
          </div>
        </header>
        <motion.main
          key={location.pathname}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -8 }}
          transition={{ duration: 0.28, ease: [0.22, 1, 0.36, 1] }}
          className="px-4 py-6 sm:px-6 lg:px-8"
        >
          <Outlet />
        </motion.main>
        </div>
      </div>
    </div>
  )
}
