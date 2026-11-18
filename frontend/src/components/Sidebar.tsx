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
} from 'lucide-react'
import { NavLink } from 'react-router-dom'

const links = [
  { to: '/', label: 'Overview', icon: LayoutDashboard },
  { to: '/messages', label: 'Message Center', icon: MessageSquare },
  { to: '/venue', label: 'Venue Planning', icon: Building2 },
  { to: '/schedule', label: 'Schedule', icon: CalendarClock },
  { to: '/food', label: 'Food Planning', icon: UtensilsCrossed },
  { to: '/judging', label: 'Judging', icon: Gavel },
  { to: '/budget', label: 'Budget Management', icon: Wallet },
  { to: '/trace', label: 'AI Agent Trace', icon: ListTree },
  { to: '/validation', label: 'Validation & Rejections', icon: ShieldAlert },
  { to: '/history', label: 'Plan Versions', icon: History },
]

export function Sidebar() {
  return (
    <aside className="w-64 shrink-0 border-r border-slate-800 bg-slate-950 p-4">
      <div className="mb-6 px-2">
        <p className="text-lg font-semibold text-white">Mind2Machine AI</p>
        <p className="text-xs text-slate-400">Intelligent Event Planning System</p>
      </div>
      <nav className="flex flex-col gap-1">
        {links.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/'}
            className={({ isActive }) =>
              `flex items-center gap-2 rounded-md px-3 py-2 text-sm ${
                isActive
                  ? 'bg-blue-600/20 text-blue-300'
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
