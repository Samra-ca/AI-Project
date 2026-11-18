import { CalendarClock } from 'lucide-react'
import { useEffect, useState } from 'react'
import { PageHeader } from '../components/PageHeader'
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
      <PageHeader icon={CalendarClock} title="Schedule Planning" subtitle="Event timetable and milestones" />
      {error && <p className="mb-4 text-sm text-red-500">{error}</p>}

      <div className="mb-4 divide-y divide-slate-100 rounded-xl border border-slate-200 bg-white shadow-sm">
        {schedule?.milestones.map(([time, activity], i) => (
          <div key={i} className="flex gap-4 px-4 py-3 text-sm">
            <span className="w-36 shrink-0 font-medium text-violet-600">{time ?? '—'}</span>
            <span className="text-slate-700">{activity}</span>
          </div>
        ))}
      </div>

      {schedule?.warnings.map((warning, i) => (
        <p
          key={i}
          className="rounded-xl border border-amber-200 bg-amber-50 p-3 text-xs text-amber-800"
        >
          {warning}
        </p>
      ))}
    </div>
  )
}
