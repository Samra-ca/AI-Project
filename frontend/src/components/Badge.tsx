type BadgeTone = 'green' | 'amber' | 'red' | 'violet' | 'slate'

const toneClasses: Record<BadgeTone, string> = {
  green: 'bg-emerald-50 text-emerald-700 ring-emerald-600/20',
  amber: 'bg-amber-50 text-amber-700 ring-amber-600/20',
  red: 'bg-red-50 text-red-700 ring-red-600/20',
  violet: 'bg-violet-50 text-violet-700 ring-violet-600/20',
  slate: 'bg-slate-100 text-slate-600 ring-slate-500/20',
}

export function Badge({ tone, children }: { tone: BadgeTone; children: React.ReactNode }) {
  return (
    <span
      className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ring-1 ring-inset ${toneClasses[tone]}`}
    >
      {children}
    </span>
  )
}

export function statusTone(status: string): BadgeTone {
  switch (status) {
    case 'accepted':
    case 'approved':
    case 'completed':
      return 'green'
    case 'rejected':
      return 'red'
    case 'pending':
    case 'partially_accepted':
    case 'in_progress':
      return 'amber'
    default:
      return 'slate'
  }
}
