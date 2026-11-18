import { Badge, statusTone } from './Badge'

interface MessageRow {
  id: string
  sender: string
  date: string
  content: string
  status: 'accepted' | 'partially_accepted' | 'rejected' | 'pending'
}

export function MessageTable({ rows }: { rows: MessageRow[] }) {
  return (
    <div className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
      <table className="w-full text-left text-sm">
        <thead className="border-b border-slate-200 bg-slate-50 text-slate-500">
          <tr>
            <th className="px-4 py-2 font-medium">Sender</th>
            <th className="px-4 py-2 font-medium">Date</th>
            <th className="px-4 py-2 font-medium">Message</th>
            <th className="px-4 py-2 font-medium">Status</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100 text-slate-700">
          {rows.map((row) => (
            <tr key={row.id}>
              <td className="px-4 py-3 whitespace-nowrap">{row.sender}</td>
              <td className="px-4 py-3 whitespace-nowrap text-slate-400">{row.date}</td>
              <td className="px-4 py-3">{row.content}</td>
              <td className="px-4 py-3">
                <Badge tone={statusTone(row.status)}>{row.status}</Badge>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
