import { useEffect, useState } from 'react'
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
      <h1 className="mb-4 text-xl font-semibold text-white">Food Planning</h1>
      {error && <p className="text-sm text-red-400">{error}</p>}
      {food?.selected && (
        <div className="mb-4 rounded-lg border border-blue-800 bg-blue-950/40 p-4">
          <p className="text-sm font-medium text-white">
            Selected: {food.selected.name} (Rs. {food.selected.price_per_person}/head x{' '}
            {food.headcount} = Rs. {food.total_cost.toLocaleString()})
          </p>
          <p className="mt-1 text-xs text-slate-400">{food.reason}</p>
        </div>
      )}
      <h2 className="mb-2 text-sm font-medium text-slate-300">Other Options</h2>
      <ul className="space-y-1 text-sm text-slate-400">
        {food?.rejected.map(([pkg, reason]) => (
          <li key={pkg.name}>
            {pkg.name} (Rs. {pkg.price_per_person}/head) - {reason}
          </li>
        ))}
      </ul>
    </div>
  )
}
