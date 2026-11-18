import { TraceTable } from '../components/TraceTable'

export function Trace() {
  return (
    <div>
      <h1 className="mb-4 text-xl font-semibold text-white">AI Agent Trace</h1>
      <TraceTable rows={[]} />
    </div>
  )
}
