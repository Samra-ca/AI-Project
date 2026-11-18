import { useEffect, useState } from 'react'
import { api } from '../services/api'
import { StatCard } from '../components/StatCard'

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
      <h1 className="mb-4 text-xl font-semibold text-white">Judging Management</h1>
      {error && <p className="text-sm text-red-400">{error}</p>}
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
          <p className="mt-4 text-sm text-slate-300">
            Capacity for {judging.capacity_teams} teams ({judging.confirmed_judges} judges x{' '}
            {judging.max_teams_per_judge} teams each) -{' '}
            {judging.is_sufficient ? 'sufficient' : 'insufficient'} for {judging.teams} teams.
          </p>
          {judging.reassignment_notes.map((note, i) => (
            <p
              key={i}
              className="mt-2 rounded-lg border border-amber-800 bg-amber-950/40 p-3 text-xs text-amber-300"
            >
              {note}
            </p>
          ))}
        </>
      )}
    </div>
  )
}
