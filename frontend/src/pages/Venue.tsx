import { useEffect, useState } from 'react'
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
      <h1 className="mb-4 text-xl font-semibold text-white">Venue Planning</h1>
      {error && <p className="text-sm text-red-400">{error}</p>}
      {venue?.selected && (
        <div className="mb-4 rounded-lg border border-blue-800 bg-blue-950/40 p-4">
          <p className="text-sm font-medium text-white">
            Selected: {venue.selected.name} (capacity {venue.selected.capacity}, Rs.{' '}
            {venue.selected.cost.toLocaleString()})
          </p>
          <p className="mt-1 text-xs text-slate-400">{venue.reason}</p>
        </div>
      )}
      <h2 className="mb-2 text-sm font-medium text-slate-300">Rejected Options</h2>
      <ul className="space-y-1 text-sm text-slate-400">
        {venue?.rejected.map(([option, reason]) => (
          <li key={option.name}>
            {option.name} (capacity {option.capacity}, Rs. {option.cost.toLocaleString()}) -{' '}
            {reason}
          </li>
        ))}
      </ul>
    </div>
  )
}
