import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from 'recharts'

interface BudgetChartProps {
  spent: number
  approved: number
}

export function BudgetChart({ spent, approved }: BudgetChartProps) {
  const remaining = Math.max(approved - spent, 0)
  const data = [
    { name: 'Spent', value: spent },
    { name: 'Remaining', value: remaining },
  ]
  const colors = ['#7c3aed', '#e2e8f0']

  return (
    <ResponsiveContainer width="100%" height={220}>
      <PieChart>
        <Pie data={data} dataKey="value" innerRadius={60} outerRadius={90}>
          {data.map((entry, index) => (
            <Cell key={entry.name} fill={colors[index]} />
          ))}
        </Pie>
        <Tooltip />
      </PieChart>
    </ResponsiveContainer>
  )
}
