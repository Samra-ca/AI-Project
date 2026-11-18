import { BudgetChart } from '../components/BudgetChart'

export function Budget() {
  return (
    <div>
      <h1 className="mb-4 text-xl font-semibold text-white">Budget Management</h1>
      <BudgetChart spent={0} approved={650000} />
    </div>
  )
}
