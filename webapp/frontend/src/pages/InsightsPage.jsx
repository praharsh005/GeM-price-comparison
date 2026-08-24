import { useEffect, useState } from 'react'
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import { Loader2, Package, TrendingDown, TrendingUp } from 'lucide-react'

import { listCategories } from '../api'

function InsightCard({ name, count, avg }) {
  const hasAvg = avg !== null && avg !== undefined
  const isSavings = hasAvg && avg > 0
  return (
    <div
      className={
        isSavings
          ? 'rounded-xl border border-[#15803D]/20 bg-white p-5 shadow-sm'
          : hasAvg
            ? 'rounded-xl border border-[#B45309]/20 bg-white p-5 shadow-sm'
            : 'rounded-xl border border-[#D9E0E8] bg-white p-5 shadow-sm'
      }
    >
      <div className="flex items-center justify-between">
        <div className="text-sm font-medium text-[#526071]">{name}</div>
        <Package className="h-4 w-4 text-[#718096]" />
      </div>
      <div className="mt-2 text-3xl font-bold text-[#172033]">{count} products</div>
      <div className="mt-2 flex items-center gap-1.5 text-sm">
        {hasAvg ? (
          <>
            {isSavings ? (
              <TrendingDown className="h-4 w-4 text-[#15803D]" />
            ) : (
              <TrendingUp className="h-4 w-4 text-[#B45309]" />
            )}
            <span className={isSavings ? 'font-semibold text-[#15803D]' : 'font-semibold text-[#B45309]'}>
              Avg {Math.abs(avg).toFixed(1)}% {isSavings ? 'cheaper on GeM' : 'costlier on GeM'}
            </span>
          </>
        ) : (
          <span className="text-[#718096]">No market prices to compare yet</span>
        )}
      </div>
    </div>
  )
}

export default function InsightsPage() {
  const [categories, setCategories] = useState([])
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let alive = true
    listCategories()
      .then((data) => alive && setCategories(data.categories))
      .catch(() => alive && setError('Unable to load insights. Is the backend running?'))
      .finally(() => alive && setLoading(false))
    return () => {
      alive = false
    }
  }, [])

  if (loading) {
    return (
      <main className="mx-auto flex max-w-5xl flex-col items-center px-6 py-16">
        <Loader2 className="h-6 w-6 animate-spin text-[#123B66]" role="status" aria-label="Loading insights" />
      </main>
    )
  }

  if (error) {
    return (
      <main className="mx-auto max-w-5xl px-6 py-16">
        <p className="text-[#B91C1C]">{error}</p>
      </main>
    )
  }

  const chartData = categories
    .filter((c) => c.avg_savings !== null && c.avg_savings !== undefined)
    .map((c) => ({ name: c.name, savings: c.avg_savings }))

  return (
    <main className="mx-auto max-w-5xl px-6 py-10">
      <h1 className="text-3xl font-bold tracking-tight text-[#172033]">Category insights</h1>
      <p className="mt-1.5 text-[#526071]">
        Average GeM price difference versus the best market price, by category. Positive values
        mean GeM is cheaper.
      </p>

      <section className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {categories.map((c) => (
          <InsightCard key={c.name} name={c.name} count={c.product_count} avg={c.avg_savings} />
        ))}
      </section>

      {chartData.length > 0 && (
        <section className="mt-8 rounded-xl border border-[#D9E0E8] bg-white p-5 shadow-sm">
          <h2 className="text-base font-semibold text-[#172033]">Average savings by category</h2>
          <div className="mt-4 h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData} margin={{ top: 8, right: 16, bottom: 8, left: 8 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#D9E0E8" vertical={false} />
                <XAxis dataKey="name" stroke="#718096" fontSize={12} tickLine={false} axisLine={false} />
                <YAxis
                  tickFormatter={(v) => `${v}%`}
                  stroke="#718096"
                  fontSize={11}
                  width={48}
                  tickLine={false}
                  axisLine={false}
                />
                <Tooltip formatter={(v) => `${v}%`} cursor={{ fill: '#F6F8FB' }} />
                <Legend wrapperStyle={{ fontSize: 12 }} />
                <Bar dataKey="savings" radius={[6, 6, 0, 0]}>
                  {chartData.map((entry) => (
                    <Cell key={entry.name} fill={entry.savings > 0 ? '#15803D' : '#B45309'} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
          <p className="mt-2 text-xs text-[#718096]">
            Green = GeM is cheaper on average · Amber = market is cheaper on average
          </p>
        </section>
      )}

      <p className="mt-10 text-xs text-[#718096]">
        Analyses are algorithmic and informational; not official recommendations.
      </p>
    </main>
  )
}