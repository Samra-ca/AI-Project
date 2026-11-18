import { LayoutDashboard, RefreshCw, Users, Wallet, Gavel, Users2 } from 'lucide-react'
import { useState } from 'react'
import { PageHeader } from '../components/PageHeader'
import { StatCard } from '../components/StatCard'
import { useDashboard } from '../hooks/useDashboard'
import { api } from '../services/api'

export function Dashboard() {
  const { stats, error, refetch } = useDashboard()
  const [running, setRunning] = useState(false)
  const [runError, setRunError] = useState<string | null>(null)

  async function handleRun() {
    setRunning(true)
    setRunError(null)
    try {
      await api.runPlan()
      await refetch()
    } catch (err) {
      setRunError(err instanceof Error ? err.message : 'Run failed')
    } finally {
      setRunning(false)
    }
  }

  return (
    <div>
      <PageHeader
        icon={LayoutDashboard}
        title="Overview Dashboard"
        subtitle="Complete overview of your AI-powered event planning"
        action={
          <button
            type="button"
            onClick={handleRun}
            disabled={running}
            className="flex items-center gap-2 rounded-lg bg-white/15 px-4 py-2 text-sm font-medium text-white hover:bg-white/25 disabled:opacity-60"
          >
            <RefreshCw size={16} className={running ? 'animate-spin' : ''} />
            {running ? 'Running...' : 'Re-run Plan'}
          </button>
        }
      />
      {error && <p className="mb-4 text-sm text-red-500">{error}</p>}
      {runError && <p className="mb-4 text-sm text-red-500">{runError}</p>}
      <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
        <StatCard label="Students" value={String(stats?.totalStudents ?? '-')} icon={Users} />
        <StatCard label="Teams" value={String(stats?.totalTeams ?? '-')} icon={Users2} />
        <StatCard
          label="Budget"
          value={stats ? `Rs. ${stats.approvedBudget.toLocaleString()}` : '-'}
          icon={Wallet}
        />
        <StatCard label="Judges" value={String(stats?.judgeCount ?? '-')} icon={Gavel} />
      </div>
      {stats && (
        <div className="mt-6 grid gap-4 md:grid-cols-3">
          <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
            <p className="text-sm text-slate-500">Estimated Expenditure</p>
            <p className="mt-1 text-xl font-semibold text-slate-900">
              Rs. {stats.estimatedExpenditure.toLocaleString()}
            </p>
          </div>
          <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
            <p className="text-sm text-slate-500">Remaining Budget</p>
            <p className="mt-1 text-xl font-semibold text-emerald-600">
              Rs. {stats.remainingBudget.toLocaleString()}
            </p>
          </div>
          <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
            <p className="text-sm text-slate-500">Messages Processed</p>
            <p className="mt-1 text-xl font-semibold text-slate-900">
              {stats.processedMessages}{' '}
              <span className="text-sm font-normal text-slate-400">
                ({stats.acceptedMessages} accepted, {stats.rejectedMessages} rejected)
              </span>
            </p>
          </div>
        </div>
      )}
    </div>
  )
}
