import type { ModelTraceEntry } from '../types'

export function TraceTable({ rows }: { rows: ModelTraceEntry[] }) {
  return (
    <div className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
      <table className="w-full text-left text-sm">
        <thead className="border-b border-slate-200 bg-slate-50 text-slate-500">
          <tr>
            <th className="px-4 py-2 font-medium">#</th>
            <th className="px-4 py-2 font-medium">Model</th>
            <th className="px-4 py-2 font-medium">Area</th>
            <th className="px-4 py-2 font-medium">Input Tokens</th>
            <th className="px-4 py-2 font-medium">Output Tokens</th>
            <th className="px-4 py-2 font-medium">Total</th>
            <th className="px-4 py-2 font-medium">Duration (ms)</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100 text-slate-700">
          {rows.map((row) => (
            <tr key={row.callNumber}>
              <td className="px-4 py-3">{row.callNumber}</td>
              <td className="px-4 py-3">{row.modelName}</td>
              <td className="px-4 py-3 capitalize">{row.area}</td>
              <td className="px-4 py-3">{row.inputTokens}</td>
              <td className="px-4 py-3">{row.outputTokens}</td>
              <td className="px-4 py-3">{row.totalTokens}</td>
              <td className="px-4 py-3">{row.durationMs}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
