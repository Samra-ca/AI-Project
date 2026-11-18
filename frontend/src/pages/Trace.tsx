import { useEffect, useState } from 'react'
import { TraceTable } from '../components/TraceTable'
import { api } from '../services/api'
import type { ModelTraceEntry } from '../types'

export function Trace() {
  const [rows, setRows] = useState<ModelTraceEntry[]>([])
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    api
      .getTrace()
      .then((data) => setRows(data as ModelTraceEntry[]))
      .catch((err: Error) => setError(err.message))
  }, [])

  const totalTokens = rows.reduce((sum, r) => sum + r.totalTokens, 0)

  return (
    <div>
      <h1 className="mb-4 text-xl font-semibold text-white">AI Agent Trace</h1>
      {error && <p className="text-sm text-red-400">{error}</p>}
      <p className="mb-4 text-sm text-slate-400">
        {rows.length} model call(s), {totalTokens.toLocaleString()} total tokens
      </p>
      <TraceTable rows={rows} />
    </div>
  )
}
