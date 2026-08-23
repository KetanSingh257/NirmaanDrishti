import { Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import {
  ArrowRight,
  BarChart3,
  Bell,
  CreditCard,
  Gauge,
  LayoutDashboard,
  Search,
  ShieldAlert,
  TrendingUp,
  Wallet,
} from 'lucide-react'
import { fetchDashboard } from '../lib/api'
import { compactInr } from '../lib/format'

const stats = [
  { label: 'Live Projects', value: '300+', icon: LayoutDashboard },
  { label: 'Risk Signals', value: '100+', icon: Bell },
  { label: 'AI Engines', value: '3', icon: Gauge },
]

export default function Landing() {
  const dash = useQuery({ queryKey: ['dashboard'], queryFn: fetchDashboard })
  const portfolioCost = dash.data ? compactInr(dash.data.total_project_value_cr) : 'Rs 56.3K Cr'

  return (
    <div className="min-h-screen overflow-hidden bg-[#3154ff] text-white">
      <div className="relative mx-auto flex min-h-screen max-w-7xl flex-col px-5 pb-8 pt-5 sm:px-8">
        <Decor />

        <header className="relative z-10 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-white text-[#3154ff] shadow-card">
              <ShieldAlert className="h-5 w-5" />
            </div>
            <div>
              <p className="font-display text-sm font-semibold tracking-wide">NIRMAANDRISHTI</p>
              <p className="font-mono text-[9px] uppercase tracking-[0.24em] text-white/70">
                Project Sentinel AI
              </p>
            </div>
          </div>
          <Link
            to="/app/dashboard"
            className="inline-flex items-center justify-center rounded-lg bg-white px-4 py-2 text-sm font-semibold text-[#3154ff] shadow-card transition hover:bg-[#f4f7ff]"
          >
            Open Dashboard
          </Link>
        </header>

        <main className="relative z-10 flex flex-1 flex-col items-center justify-center gap-9 py-10">
          <motion.section
            initial={{ opacity: 0, y: 18 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center"
          >
            <h1 className="mx-auto max-w-5xl font-display text-5xl font-semibold leading-none tracking-normal sm:text-7xl lg:text-[86px]">
              Free Dashboard Ui Kit
            </h1>
            <div className="mt-6 flex flex-wrap justify-center gap-4">
              <FeaturePill>300+ Layouts</FeaturePill>
              <FeaturePill>Top Trending</FeaturePill>
              <FeaturePill>100+ Components</FeaturePill>
            </div>
          </motion.section>

          <motion.section
            initial={{ opacity: 0, y: 26 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.12 }}
            className="relative w-full max-w-5xl"
          >
            <div className="absolute -left-4 bottom-14 hidden rounded-xl bg-white p-3 text-[#16204a] shadow-card md:block">
              <p className="text-xs font-semibold">Overall cost</p>
              <p className="mt-1 text-xl font-bold">{portfolioCost}</p>
              <div className="mt-3 h-20 w-48 rounded-lg bg-[#f4f7ff] p-3">
                <div className="flex h-full items-end gap-2">
                  {[42, 64, 36, 78, 54, 88].map((h, i) => (
                    <span
                      key={i}
                      className="flex-1 rounded-t bg-[#3154ff]"
                      style={{ height: `${h}%`, opacity: 0.25 + i * 0.11 }}
                    />
                  ))}
                </div>
              </div>
            </div>

            <div className="absolute -right-3 bottom-0 hidden w-56 rounded-xl bg-white p-4 text-[#16204a] shadow-card lg:block">
              <p className="mb-3 text-sm font-semibold">Risk split</p>
              <div className="mx-auto grid h-28 w-28 place-items-center rounded-full bg-[conic-gradient(#3154ff_0_55%,#21c7d9_55%_78%,#ffb020_78%_100%)]">
                <div className="grid h-16 w-16 place-items-center rounded-full bg-white text-sm font-bold">
                  55%
                </div>
              </div>
            </div>

            <div className="overflow-hidden rounded-xl bg-white text-[#16204a] shadow-[0_40px_100px_-45px_rgba(10,24,120,0.9)]">
              <div className="flex h-14 items-center justify-between border-b border-[#e7ecff] px-5">
                <div className="flex items-center gap-2">
                  <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-[#3154ff] text-white">
                    <Wallet className="h-4 w-4" />
                  </div>
                  <span className="font-display text-sm font-semibold">DashStack</span>
                </div>
                <div className="hidden w-64 items-center gap-2 rounded-full bg-[#f4f7ff] px-4 py-2 text-xs text-[#637097] sm:flex">
                  <Search className="h-3.5 w-3.5" />
                  Search for insights
                </div>
                <div className="flex items-center gap-3 text-[#637097]">
                  <Bell className="h-4 w-4" />
                  <div className="h-8 w-8 rounded-full bg-[#f1c9b7]" />
                </div>
              </div>

              <div className="grid min-h-[420px] grid-cols-[78px_1fr] sm:grid-cols-[190px_1fr]">
                <aside className="border-r border-[#e7ecff] bg-[#fbfcff] p-4">
                  <p className="hidden font-display text-xs font-semibold text-[#3154ff] sm:block">
                    Overview
                  </p>
                  <div className="mt-5 space-y-2">
                    {['Dashboard', 'Projects', 'Analytics', 'Risks', 'Reports'].map((item, index) => (
                      <div
                        key={item}
                        className={`flex items-center gap-3 rounded-lg px-3 py-2 text-xs ${
                          index === 0 ? 'bg-[#3154ff] text-white' : 'text-[#8c97bb]'
                        }`}
                      >
                        <LayoutDashboard className="h-4 w-4" />
                        <span className="hidden sm:inline">{item}</span>
                      </div>
                    ))}
                  </div>
                </aside>

                <div className="bg-[#f7f9ff] p-4 sm:p-6">
                  <div className="mb-5 flex items-end justify-between">
                    <div>
                      <p className="font-display text-xl font-semibold">Dashboard</p>
                      <p className="text-xs text-[#637097]">Live infrastructure intelligence</p>
                    </div>
                    <Link
                      to="/app/dashboard"
                      className="hidden items-center gap-2 rounded-lg bg-[#3154ff] px-4 py-2 text-sm font-semibold text-white sm:inline-flex"
                    >
                      Explore <ArrowRight className="h-4 w-4" />
                    </Link>
                  </div>

                  <div className="grid gap-4 md:grid-cols-3">
                    {stats.map((s) => (
                      <div key={s.label} className="rounded-xl bg-white p-4 shadow-sm">
                        <div className="mb-4 flex items-center justify-between">
                          <span className="text-xs text-[#637097]">{s.label}</span>
                          <span className="grid h-9 w-9 place-items-center rounded-lg bg-[#eef3ff] text-[#3154ff]">
                            <s.icon className="h-4 w-4" />
                          </span>
                        </div>
                        <p className="font-display text-2xl font-semibold">{s.value}</p>
                        <p className="mt-2 text-xs text-[#19c37d]">Up from last review</p>
                      </div>
                    ))}
                  </div>

                  <div className="mt-5 grid gap-4 lg:grid-cols-[1.5fr_1fr]">
                    <div className="rounded-xl bg-white p-5 shadow-sm">
                      <div className="mb-4 flex items-center justify-between">
                        <p className="font-display font-semibold">Progress Details</p>
                        <TrendingUp className="h-5 w-5 text-[#3154ff]" />
                      </div>
                      <div className="relative h-44 overflow-hidden rounded-lg bg-[#f8faff]">
                        <div className="absolute inset-x-0 bottom-0 h-28 bg-gradient-to-t from-[#3154ff]/15 to-transparent" />
                        <svg viewBox="0 0 520 170" className="absolute inset-0 h-full w-full">
                          <polyline
                            points="0,130 45,112 90,116 135,82 180,96 225,50 270,88 315,63 360,82 405,48 450,72 520,58"
                            fill="none"
                            stroke="#3154ff"
                            strokeWidth="5"
                            strokeLinecap="round"
                            strokeLinejoin="round"
                          />
                        </svg>
                      </div>
                    </div>

                    <div className="rounded-xl bg-white p-5 shadow-sm">
                      <p className="font-display font-semibold">Recent Signals</p>
                      <div className="mt-4 space-y-3">
                        {['Cost acceleration', 'Timeline variance', 'Trend improving'].map((item, i) => (
                          <div key={item} className="flex items-center gap-3">
                            <span className="grid h-9 w-9 place-items-center rounded-lg bg-[#eef3ff] text-[#3154ff]">
                              <BarChart3 className="h-4 w-4" />
                            </span>
                            <div>
                              <p className="text-sm font-semibold">{item}</p>
                              <p className="text-xs text-[#637097]">{i + 2} projects updated</p>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div className="mx-auto -mt-9 flex w-fit gap-4 rounded-full bg-[#3154ff] px-5 py-3 shadow-card">
              {[CreditCard, Wallet, LayoutDashboard, Gauge].map((Icon, i) => (
                <span key={i} className="grid h-14 w-14 place-items-center rounded-full bg-white text-[#3154ff]">
                  <Icon className="h-6 w-6" />
                </span>
              ))}
            </div>
          </motion.section>
        </main>
      </div>
    </div>
  )
}

function FeaturePill({ children }: { children: React.ReactNode }) {
  return (
    <span className="rounded-lg bg-white/20 px-5 py-2 font-display text-xl font-semibold text-white shadow-card backdrop-blur">
      {children}
    </span>
  )
}

function Decor() {
  return (
    <div className="pointer-events-none absolute inset-0 overflow-hidden">
      <div className="absolute -right-16 top-32 h-72 w-72 rounded-full border border-white/10" />
      <div className="absolute -right-8 top-40 h-56 w-56 rounded-full border border-white/10" />
      <div className="absolute left-0 top-[46%] grid grid-cols-7 gap-2 opacity-70">
        {Array.from({ length: 49 }).map((_, i) => (
          <span key={i} className="h-1.5 w-1.5 rounded-full bg-[#ffcc33]" />
        ))}
      </div>
      <div className="absolute right-4 top-[35%] grid grid-cols-6 gap-2 opacity-70">
        {Array.from({ length: 36 }).map((_, i) => (
          <span key={i} className="h-1.5 w-1.5 rounded-full bg-[#ffcc33]" />
        ))}
      </div>
    </div>
  )
}
