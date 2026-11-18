interface MessageRow {
  id: string
  sender: string
  date: string
  content: string
  status: 'accepted' | 'partially_accepted' | 'rejected' | 'pending'
}

export function MessageTable({ rows }: { rows: MessageRow[] }) {
  return (
    <table className="w-full text-left text-sm">
      <thead className="text-slate-400">
        <tr>
          <th className="py-2">Sender</th>
          <th className="py-2">Date</th>
          <th className="py-2">Message</th>
          <th className="py-2">Status</th>
        </tr>
      </thead>
      <tbody className="text-slate-200">
        {rows.map((row) => (
          <tr key={row.id} className="border-t border-slate-800">
            <td className="py-2">{row.sender}</td>
            <td className="py-2">{row.date}</td>
            <td className="py-2">{row.content}</td>
            <td className="py-2">{row.status}</td>
          </tr>
        ))}
      </tbody>
    </table>
  )
}
