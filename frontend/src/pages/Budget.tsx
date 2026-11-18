import { Wallet } from 'lucide-react'
import { useEffect, useState } from 'react'
import { Badge } from '../components/Badge'
import { BudgetChart } from '../components/BudgetChart'
import { PageHeader } from '../components/PageHeader'
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
      <PageHeader
        icon={Wallet}
        title="Budget Management"
        subtitle="Track and manage event expenses"
        action={
          budget && (
            <Badge tone={budget.within_budget ? 'green' : 'red'}>
              {budget.within_budget ? 'Within budget' : 'Over budget'}
            </Badge>
          )
        }
      />
      {error && <p className="mb-4 text-sm text-red-500">{error}</p>}

      <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
        <BudgetChart
          spent={budget?.total_committed ?? 0}
          approved={budget?.approved_budget ?? 650000}
        />
      </div>

      {budget && (
        <div className="mt-4 grid gap-4 md:grid-cols-2">
          <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
            <h2 className="mb-2 text-sm font-semibold text-slate-700">Committed</h2>
            <ul className="space-y-1 text-sm">
              {budget.committed_items.map((item) => (
                <li key={item.category} className="flex justify-between text-slate-700">
                  <span>{item.category}</span>
                  <span className="font-medium">Rs. {item.amount.toLocaleString()}</span>
                </li>
              ))}
            </ul>
            <div className="mt-3 flex justify-between border-t border-slate-100 pt-2 text-sm font-semibold text-slate-900">
              <span>Total</span>
              <span>Rs. {budget.total_committed.toLocaleString()}</span>
            </div>
          </div>
          <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
            <h2 className="mb-2 text-sm font-semibold text-slate-700">Pending Approval</h2>
            <ul className="space-y-1 text-sm text-slate-500">
              {budget.pending_items.length === 0 && <li>None</li>}
              {budget.pending_items.map((item) => (
                <li key={item.category} className="flex justify-between">
                  <span>{item.category}</span>
                  <span>Rs. {item.amount.toLocaleString()}</span>
                </li>
              ))}
            </ul>
            <div className="mt-3 flex justify-between border-t border-slate-100 pt-2 text-sm font-semibold text-emerald-600">
              <span>Remaining</span>
              <span>Rs. {budget.remaining.toLocaleString()}</span>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
