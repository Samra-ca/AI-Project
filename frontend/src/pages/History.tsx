import { History as HistoryIcon } from 'lucide-react'
import { useEffect, useState } from 'react'
import { Badge } from '../components/Badge'
import { PageHeader } from '../components/PageHeader'
import { api } from '../services/api'

interface PlanVersion {
  versionNumber: number
  isCurrent: boolean
  createdAt: string
}

export function History() {
  const [versions, setVersions] = useState<PlanVersion[]>([])
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    api
      .getPlanHistory()
      .then((data) => setVersions(data as PlanVersion[]))
      .catch((err: Error) => setError(err.message))
  }, [])

  return (
    <div>
      <PageHeader icon={HistoryIcon} title="Plan History" subtitle="Every plan version generated so far" />
      {error && <p className="mb-4 text-sm text-red-500">{error}</p>}
      <div className="divide-y divide-slate-100 rounded-xl border border-slate-200 bg-white shadow-sm">
        {versions.map((v) => (
          <div key={v.versionNumber} className="flex items-center justify-between px-4 py-3 text-sm">
            <span className="font-medium text-slate-800">Version {v.versionNumber}</span>
            <span className="text-slate-400">{new Date(v.createdAt).toLocaleString()}</span>
            {v.isCurrent ? <Badge tone="violet">Current</Badge> : <Badge tone="slate">Archived</Badge>}
          </div>
        ))}
      </div>
    </div>
  )
}
