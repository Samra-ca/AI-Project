import { useEffect, useState } from 'react'
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
      <h1 className="mb-4 text-xl font-semibold text-white">Plan Versions</h1>
      {error && <p className="text-sm text-red-400">{error}</p>}
      <ul className="space-y-2">
        {versions.map((v) => (
          <li
            key={v.versionNumber}
            className="flex items-center justify-between rounded-lg border border-slate-800 bg-slate-900/60 p-3 text-sm"
          >
            <span className="text-slate-200">Version {v.versionNumber}</span>
            <span className="text-slate-400">{new Date(v.createdAt).toLocaleString()}</span>
            {v.isCurrent && (
              <span className="rounded-full bg-blue-600/20 px-2 py-0.5 text-xs text-blue-300">
                Current
              </span>
            )}
          </li>
        ))}
      </ul>
    </div>
  )
}
