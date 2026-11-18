import {
  LayoutDashboard,
  MessageSquare,
  Building2,
  CalendarClock,
  UtensilsCrossed,
  Gavel,
  Wallet,
  ListTree,
  ShieldAlert,
  History,
  Sparkles,
} from 'lucide-react'
import { NavLink } from 'react-router-dom'

const links = [
  { to: '/', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/messages', label: 'Message Center', icon: MessageSquare },
  { to: '/venue', label: 'Venue Planning', icon: Building2 },
  { to: '/schedule', label: 'Schedule Planning', icon: CalendarClock },
  { to: '/food', label: 'Food Planning', icon: UtensilsCrossed },
  { to: '/judging', label: 'Judging Management', icon: Gavel },
  { to: '/budget', label: 'Budget Management', icon: Wallet },
  { to: '/trace', label: 'AI Agent Trace', icon: ListTree },
  { to: '/validation', label: 'Validation & Rejections', icon: ShieldAlert },
  { to: '/history', label: 'Plan History', icon: History },
]

export function Sidebar() {
  return (
    <aside className="w-64 shrink-0 bg-slate-950 p-4">
      <div className="mb-6 flex items-center gap-2 px-2">
        <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-violet-600">
          <Sparkles size={18} className="text-white" />
        </div>
        <div>
          <p className="text-sm font-semibold text-white">Mind2Machine</p>
          <p className="text-xs text-slate-400">AI Event Planning Agent</p>
        </div>
      </div>
      <nav className="flex flex-col gap-1">
        {links.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/'}
            className={({ isActive }) =>
              `flex items-center gap-2 rounded-md px-3 py-2 text-sm transition-colors ${
                isActive
                  ? 'bg-violet-600 text-white'
                  : 'text-slate-300 hover:bg-slate-800'
              }`
            }
          >
            <Icon size={16} />
            {label}
          </NavLink>
        ))}
      </nav>
    </aside>
  )
}
