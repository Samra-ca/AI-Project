import { StatCard } from '../components/StatCard'
import { useDashboard } from '../hooks/useDashboard'

export function Dashboard() {
  const { stats, error } = useDashboard()

  return (
    <div>
      <h1 className="mb-4 text-xl font-semibold text-white">Overview</h1>
      {error && <p className="text-sm text-red-400">{error}</p>}
      <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
        <StatCard label="Students" value={String(stats?.totalStudents ?? '—')} />
        <StatCard label="Teams" value={String(stats?.totalTeams ?? '—')} />
        <StatCard
          label="Budget"
          value={stats ? `Rs. ${stats.approvedBudget.toLocaleString()}` : '—'}
        />
        <StatCard label="Judges" value={String(stats?.judgeCount ?? '—')} />
      </div>
    </div>
  )
}
