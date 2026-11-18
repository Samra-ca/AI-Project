import { Bell, UserRound } from 'lucide-react'

export function Navbar() {
  return (
    <header className="flex items-center justify-between border-b border-slate-200 bg-white px-6 py-3">
      <p className="text-sm text-slate-500">Mind to Machine Hackathon &middot; System Ready</p>
      <div className="flex items-center gap-3">
        <button
          type="button"
          className="rounded-full p-2 text-slate-500 hover:bg-slate-100"
          aria-label="Notifications"
        >
          <Bell size={18} />
        </button>
        <div className="flex h-8 w-8 items-center justify-center rounded-full bg-violet-600 text-white">
          <UserRound size={16} />
        </div>
      </div>
    </header>
  )
}
