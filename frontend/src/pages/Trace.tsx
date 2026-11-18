import { ListTree } from 'lucide-react'
import { useEffect, useState } from 'react'
import { PageHeader } from '../components/PageHeader'
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
      <PageHeader
        icon={ListTree}
        title="AI Agent Trace"
        subtitle={`${rows.length} model call(s), ${totalTokens.toLocaleString()} total tokens`}
      />
      {error && <p className="mb-4 text-sm text-red-500">{error}</p>}
      <TraceTable rows={rows} />
    </div>
  )
}
