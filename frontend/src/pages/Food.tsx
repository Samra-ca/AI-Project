import { UtensilsCrossed } from 'lucide-react'
import { useEffect, useState } from 'react'
import { Badge } from '../components/Badge'
import { PageHeader } from '../components/PageHeader'
import { api } from '../services/api'

interface FoodPackage {
  name: string
  price_per_person: number
  delivery_charge: number
}

interface FoodData {
  selected: FoodPackage | null
  headcount: number
  total_cost: number
  reason: string
  rejected: [FoodPackage, string][]
}

export function Food() {
  const [food, setFood] = useState<FoodData | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    api
      .getPlanCurrent()
      .then((data) => setFood((data as { food: FoodData }).food))
      .catch((err: Error) => setError(err.message))
  }, [])

  return (
    <div>
      <PageHeader icon={UtensilsCrossed} title="Food Planning" subtitle="Meals and refreshments for participants" />
      {error && <p className="mb-4 text-sm text-red-500">{error}</p>}

      {food?.selected && (
        <div className="mb-4 rounded-xl border border-violet-200 bg-violet-50 p-4">
          <div className="flex items-center justify-between">
            <p className="text-sm font-semibold text-slate-900">
              {food.selected.name} &middot; Rs. {food.selected.price_per_person}/head x{' '}
              {food.headcount} = Rs. {food.total_cost.toLocaleString()}
            </p>
            <Badge tone="violet">Selected</Badge>
          </div>
          <p className="mt-1 text-xs text-slate-600">{food.reason}</p>
        </div>
      )}

      <h2 className="mb-2 text-sm font-semibold text-slate-700">Other Options</h2>
      <div className="grid gap-3 md:grid-cols-2">
        {food?.rejected.map(([pkg, reason]) => (
          <div key={pkg.name} className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
            <div className="flex items-center justify-between">
              <p className="text-sm font-medium text-slate-800">{pkg.name}</p>
              <Badge tone="slate">Not selected</Badge>
            </div>
            <p className="mt-1 text-xs text-slate-500">Rs. {pkg.price_per_person}/head</p>
            <p className="mt-1 text-xs text-slate-400">{reason}</p>
          </div>
        ))}
      </div>
    </div>
  )
}
