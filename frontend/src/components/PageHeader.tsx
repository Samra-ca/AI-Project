import type { LucideIcon } from 'lucide-react'
import type { ReactNode } from 'react'

interface PageHeaderProps {
  icon: LucideIcon
  title: string
  subtitle?: string
  action?: ReactNode
}

export function PageHeader({ icon: Icon, title, subtitle, action }: PageHeaderProps) {
  return (
    <div className="mb-6 flex items-center justify-between rounded-xl bg-gradient-to-r from-violet-600 to-indigo-600 px-5 py-4 shadow-sm">
      <div className="flex items-center gap-3">
        <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-white/15">
          <Icon size={20} className="text-white" />
        </div>
        <div>
          <h1 className="text-base font-semibold text-white">{title}</h1>
          {subtitle && <p className="text-xs text-violet-100">{subtitle}</p>}
        </div>
      </div>
      {action}
    </div>
  )
}
