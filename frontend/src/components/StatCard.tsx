interface StatCardProps {
  label: string
  value: string
  unit?: string
}

export function StatCard({ label, value, unit }: StatCardProps) {
  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-4">
      <p className="text-sm text-slate-400">{label}</p>
      <p className="mt-1 text-2xl font-semibold text-white">
        {value}
        {unit && <span className="ml-1 text-sm text-slate-400">{unit}</span>}
      </p>
    </div>
  )
}
