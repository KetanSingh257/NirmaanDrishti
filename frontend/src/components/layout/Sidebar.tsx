import { NavLink } from 'react-router-dom'
import {
  Activity,
  AlertTriangle,
  BarChart3,
  ChevronLeft,
  Clock3,
  LayoutDashboard,
  Settings,
  Shield,
  TrendingDown,
  Wallet,
} from 'lucide-react'
import { cn } from '../../lib/utils'

const nav = [
  { to: '/app/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/app/projects', label: 'Projects', icon: Shield },
  {
    label: 'AI Intelligence',
    children: [
      { to: '/app/intelligence/cost', label: 'Cost Analysis', icon: Wallet },
      { to: '/app/intelligence/time', label: 'Time Analysis', icon: Clock3 },
      { to: '/app/intelligence/trend', label: 'Trend Analysis', icon: TrendingDown },
    ],
  },
  { to: '/app/risks', label: 'Risk Monitor', icon: AlertTriangle },
  { to: '/app/analytics', label: 'Analytics', icon: BarChart3 },
  { to: '/app/settings', label: 'Settings', icon: Settings },
]

export default function Sidebar({
  collapsed,
  onToggle,
  mobileOpen,
  onClose,
}: {
  collapsed: boolean
  onToggle: () => void
  mobileOpen: boolean
  onClose: () => void
}) {
  return (
    <>
      <div
        className={cn(
          'fixed inset-0 z-30 bg-parchment-50/35 backdrop-blur-sm lg:hidden',
          mobileOpen ? 'block' : 'hidden',
        )}
        onClick={onClose}
      />
      <aside
        className={cn(
          'fixed inset-y-0 left-0 z-40 flex flex-col border-r border-[#dfe6ff] bg-white/95 shadow-[18px_0_70px_-48px_rgba(10,24,120,0.85)] backdrop-blur-xl transition-all duration-300 lg:bottom-8 lg:left-8 lg:top-8 lg:rounded-[18px] lg:border',
          collapsed ? 'w-[76px]' : 'w-[268px]',
          mobileOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0',
        )}
      >
        <div className="flex h-16 items-center gap-3 border-b border-[#dfe6ff] px-4">
          <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-parchment-300 shadow-glow">
            <Activity className="h-4 w-4 text-white" />
          </div>
          {!collapsed && (
            <div className="min-w-0">
              <p className="truncate font-display text-[13px] font-semibold tracking-wide text-parchment-50">
                NIRMAANDRISHTI
              </p>
              <p className="font-mono text-[9px] uppercase tracking-[0.22em] text-parchment-200">
                Project Sentinel
              </p>
            </div>
          )}
        </div>

        <nav className="flex-1 space-y-1 overflow-y-auto px-3 py-4">
          {nav.map((item) =>
            'children' in item && item.children ? (
              <div key={item.label} className="pt-2">
                {!collapsed && (
                  <p className="mb-1 px-3 font-mono text-[9px] uppercase tracking-[0.22em] text-parchment-200/70">
                    {item.label}
                  </p>
                )}
                {item.children.map((child) => (
                  <Item key={child.to} {...child} collapsed={collapsed} onClick={onClose} />
                ))}
              </div>
            ) : (
              <Item key={item.to} {...(item as { to: string; label: string; icon: typeof LayoutDashboard })} collapsed={collapsed} onClick={onClose} />
            ),
          )}
        </nav>

        <button
          onClick={onToggle}
          className="hidden items-center justify-center border-t border-[#dfe6ff] py-3 text-parchment-200 hover:text-parchment-300 lg:flex"
        >
          <ChevronLeft className={cn('h-4 w-4 transition', collapsed && 'rotate-180')} />
        </button>
      </aside>
    </>
  )
}

function Item({
  to,
  label,
  icon: Icon,
  collapsed,
  onClick,
}: {
  to: string
  label: string
  icon: typeof LayoutDashboard
  collapsed: boolean
  onClick: () => void
}) {
  return (
    <NavLink
      to={to}
      onClick={onClick}
      className={({ isActive }) =>
        cn(
          'group relative flex items-center gap-3 rounded-lg px-3 py-2 text-sm transition',
          isActive
            ? 'bg-parchment-300 text-white shadow-glow'
            : 'text-parchment-200 hover:bg-parchment-300/10 hover:text-parchment-300',
        )
      }
    >
      {({ isActive }) => (
        <>
          {isActive && (
            <span className="absolute left-0 top-1/2 h-5 w-0.5 -translate-y-1/2 rounded-full bg-white" />
          )}
          <Icon className="h-4 w-4 shrink-0" />
          {!collapsed && <span>{label}</span>}
        </>
      )}
    </NavLink>
  )
}
