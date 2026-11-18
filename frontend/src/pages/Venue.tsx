import { Building2 } from 'lucide-react'
import { useEffect, useState } from 'react'
import { Badge } from '../components/Badge'
import { PageHeader } from '../components/PageHeader'
import { api } from '../services/api'

interface VenueOption {
  name: string
  capacity: number
  cost: number
  has_generator: boolean
}

interface VenueData {
  selected: VenueOption | null
  reason: string
  rejected: [VenueOption, string][]
}

export function Venue() {
  const [venue, setVenue] = useState<VenueData | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    api
      .getPlanCurrent()
      .then((data) => setVenue((data as { venue: VenueData }).venue))
      .catch((err: Error) => setError(err.message))
  }, [])

  return (
    <div>
      <PageHeader icon={Building2} title="Venue Planning" subtitle="Find and manage the best venue for your event" />
      {error && <p className="mb-4 text-sm text-red-500">{error}</p>}

      {venue?.selected && (
        <div className="mb-4 rounded-xl border border-violet-200 bg-violet-50 p-4">
          <div className="flex items-center justify-between">
            <p className="text-sm font-semibold text-slate-900">
              {venue.selected.name} &middot; capacity {venue.selected.capacity} &middot; Rs.{' '}
              {venue.selected.cost.toLocaleString()}
            </p>
            <Badge tone="violet">Recommended</Badge>
          </div>
          <p className="mt-1 text-xs text-slate-600">{venue.reason}</p>
        </div>
      )}

      <h2 className="mb-2 text-sm font-semibold text-slate-700">Other Options</h2>
      <div className="grid gap-3 md:grid-cols-2">
        {venue?.rejected.map(([option, reason]) => (
          <div
            key={option.name}
            className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm"
          >
            <div className="flex items-center justify-between">
              <p className="text-sm font-medium text-slate-800">{option.name}</p>
              <Badge tone="slate">Not selected</Badge>
            </div>
            <p className="mt-1 text-xs text-slate-500">
              Capacity {option.capacity} &middot; Rs. {option.cost.toLocaleString()}
              {option.has_generator ? ' · Generator' : ''}
            </p>
            <p className="mt-1 text-xs text-slate-400">{reason}</p>
          </div>
        ))}
      </div>
    </div>
  )
}
