import type { ModelTraceEntry } from '../types'

export function TraceTable({ rows }: { rows: ModelTraceEntry[] }) {
  return (
    <table className="w-full text-left text-sm">
      <thead className="text-slate-400">
        <tr>
          <th className="py-2">#</th>
          <th className="py-2">Model</th>
          <th className="py-2">Area</th>
          <th className="py-2">Input Tokens</th>
          <th className="py-2">Output Tokens</th>
          <th className="py-2">Total</th>
          <th className="py-2">Duration (ms)</th>
        </tr>
      </thead>
      <tbody className="text-slate-200">
        {rows.map((row) => (
          <tr key={row.callNumber} className="border-t border-slate-800">
            <td className="py-2">{row.callNumber}</td>
            <td className="py-2">{row.modelName}</td>
            <td className="py-2">{row.area}</td>
            <td className="py-2">{row.inputTokens}</td>
            <td className="py-2">{row.outputTokens}</td>
            <td className="py-2">{row.totalTokens}</td>
            <td className="py-2">{row.durationMs}</td>
          </tr>
        ))}
      </tbody>
    </table>
  )
}
