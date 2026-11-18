import { Gavel } from 'lucide-react'
import { useEffect, useState } from 'react'
import { Badge } from '../components/Badge'
import { PageHeader } from '../components/PageHeader'
import { StatCard } from '../components/StatCard'
import { api } from '../services/api'

interface JudgingData {
  teams: number
  confirmed_judges: number
  minutes_per_team: number
  max_teams_per_judge: number
  min_required_judges: number
  capacity_teams: number
  is_sufficient: boolean
  honorarium_total: number
  reassignment_notes: string[]
}

export function Judging() {
  const [judging, setJudging] = useState<JudgingData | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    api
      .getPlanCurrent()
      .then((data) => setJudging((data as { judging: JudgingData }).judging))
      .catch((err: Error) => setError(err.message))
  }, [])

  return (
    <div>
      <PageHeader icon={Gavel} title="Judging Management" subtitle="Judges, capacity, and assignments" />
      {error && <p className="mb-4 text-sm text-red-500">{error}</p>}
      {judging && (
        <>
          <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
            <StatCard label="Teams" value={String(judging.teams)} />
            <StatCard label="Confirmed Judges" value={String(judging.confirmed_judges)} />
            <StatCard label="Min Required" value={String(judging.min_required_judges)} />
            <StatCard
              label="Honorarium Total"
              value={`Rs. ${judging.honorarium_total.toLocaleString()}`}
            />
          </div>
          <div className="mt-4 flex items-center justify-between rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
            <p className="text-sm text-slate-700">
              Capacity for {judging.capacity_teams} teams ({judging.confirmed_judges} judges x{' '}
              {judging.max_teams_per_judge} teams each, {judging.minutes_per_team} min/team) for{' '}
              {judging.teams} teams needed.
            </p>
            <Badge tone={judging.is_sufficient ? 'green' : 'red'}>
              {judging.is_sufficient ? 'Sufficient' : 'Insufficient'}
            </Badge>
          </div>
          {judging.reassignment_notes.map((note, i) => (
            <p
              key={i}
              className="mt-3 rounded-xl border border-amber-200 bg-amber-50 p-3 text-xs text-amber-800"
            >
              {note}
            </p>
          ))}
        </>
      )}
    </div>
  )
}
