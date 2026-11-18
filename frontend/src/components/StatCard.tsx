import type { LucideIcon } from 'lucide-react'

interface StatCardProps {
  label: string
  value: string
  unit?: string
  icon?: LucideIcon
}

export function StatCard({ label, value, unit, icon: Icon }: StatCardProps) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
      <div className="flex items-center justify-between">
        <p className="text-sm text-slate-500">{label}</p>
        {Icon && (
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-violet-50">
            <Icon size={16} className="text-violet-600" />
          </div>
        )}
      </div>
      <p className="mt-1 text-2xl font-semibold text-slate-900">
        {value}
        {unit && <span className="ml-1 text-sm font-normal text-slate-400">{unit}</span>}
      </p>
    </div>
  )
}
