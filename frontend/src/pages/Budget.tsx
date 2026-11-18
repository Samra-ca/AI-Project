import { useEffect, useState } from 'react'
import { BudgetChart } from '../components/BudgetChart'
import { api } from '../services/api'

interface BudgetLineItem {
  category: string
  amount: number
  approved: boolean
}

interface BudgetData {
  approved_budget: number
  committed_items: BudgetLineItem[]
  pending_items: BudgetLineItem[]
  total_committed: number
  remaining: number
  within_budget: boolean
}

export function Budget() {
  const [budget, setBudget] = useState<BudgetData | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    api
      .getBudget()
      .then((data) => setBudget(data as BudgetData))
      .catch((err: Error) => setError(err.message))
  }, [])

  return (
    <div>
      <h1 className="mb-4 text-xl font-semibold text-white">Budget Management</h1>
      {error && <p className="text-sm text-red-400">{error}</p>}
      <BudgetChart
        spent={budget?.total_committed ?? 0}
        approved={budget?.approved_budget ?? 650000}
      />
      {budget && (
        <div className="mt-4 grid gap-4 md:grid-cols-2">
          <div>
            <h2 className="mb-2 text-sm font-medium text-slate-300">Committed</h2>
            <ul className="space-y-1 text-sm text-slate-200">
              {budget.committed_items.map((item) => (
                <li key={item.category} className="flex justify-between">
                  <span>{item.category}</span>
                  <span>Rs. {item.amount.toLocaleString()}</span>
                </li>
              ))}
            </ul>
          </div>
          <div>
            <h2 className="mb-2 text-sm font-medium text-slate-300">Pending Approval</h2>
            <ul className="space-y-1 text-sm text-slate-400">
              {budget.pending_items.length === 0 && <li>None</li>}
              {budget.pending_items.map((item) => (
                <li key={item.category} className="flex justify-between">
                  <span>{item.category}</span>
                  <span>Rs. {item.amount.toLocaleString()}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}
    </div>
  )
}
