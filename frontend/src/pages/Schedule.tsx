import { useEffect, useState } from 'react'
import { api } from '../services/api'

interface ScheduleData {
  milestones: [string | null, string][]
  prayer_break_minutes: number | null
  stated_duration_minutes: number | null
  warnings: string[]
}

export function Schedule() {
  const [schedule, setSchedule] = useState<ScheduleData | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    api
      .getPlanCurrent()
      .then((data) => setSchedule((data as { schedule: ScheduleData }).schedule))
      .catch((err: Error) => setError(err.message))
  }, [])

  return (
    <div>
      <h1 className="mb-4 text-xl font-semibold text-white">Schedule Planning</h1>
      {error && <p className="text-sm text-red-400">{error}</p>}
      <ul className="mb-4 space-y-1 text-sm text-slate-200">
        {schedule?.milestones.map(([time, activity], i) => (
          <li key={i} className="flex gap-3">
            <span className="w-32 text-slate-400">{time ?? '—'}</span>
            <span>{activity}</span>
          </li>
        ))}
      </ul>
      {schedule?.warnings.map((warning, i) => (
        <p key={i} className="rounded-lg border border-amber-800 bg-amber-950/40 p-3 text-xs text-amber-300">
          {warning}
        </p>
      ))}
    </div>
  )
}
