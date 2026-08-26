import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'

import { formatDate, formatINR } from '../utils/format'

const LINE_COLORS = ['#123B66', '#0F766E', '#B45309', '#15803D', '#6D28D9', '#B91C1C']

function toSeries(listings, priceHistory) {
  const nameByListing = new Map(listings.map((l) => [String(l.id), l.marketplace_name]))
  const points = []
  for (const [listingId, history] of Object.entries(priceHistory || {})) {
    const seriesName = nameByListing.get(listingId) || `Listing ${listingId}`
    for (const point of history) {
      points.push({
        time: new Date(point.recorded_at).getTime(),
        seriesName,
        price: point.price,
      })
    }
  }
  points.sort((a, b) => a.time - b.time)
  return points
}

export default function PriceTrendChart({ listings, priceHistory }) {
  const points = toSeries(listings, priceHistory)
  if (points.length === 0) return null

  const series = [...new Set(points.map((p) => p.seriesName))]
  // merge the per-series points onto a shared time axis for Recharts
  const times = [...new Set(points.map((p) => p.time))].sort((a, b) => a - b)
  const data = times.map((t) => {
    const row = { time: t }
    for (const name of series) {
      const hit = points.find((p) => p.time === t && p.seriesName === name)
      if (hit) row[name] = hit.price
    }
    return row
  })

  return (
    <section className="mt-8 rounded-xl border border-[#D9E0E8] bg-white p-4">
      <h2 className="text-base font-semibold text-[#172033]">Price trend</h2>
      <p className="mt-1 text-sm text-[#718096]">
        Historical price snapshots across marketplaces.
      </p>
      <div className="mt-4 h-72">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data} margin={{ top: 8, right: 16, bottom: 8, left: 8 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#D9E0E8" />
            <XAxis
              dataKey="time"
              tickFormatter={(ts) => formatDate(ts)}
              stroke="#718096"
              fontSize={11}
              minTickGap={40}
            />
            <YAxis
              tickFormatter={(v) => `₹${Number(v).toLocaleString('en-IN')}`}
              stroke="#718096"
              fontSize={11}
              width={70}
            />
            <Tooltip
              formatter={(value) => formatINR(value)}
              labelFormatter={(ts) => formatDate(ts)}
            />
            <Legend wrapperStyle={{ fontSize: 12 }} />
            {series.map((name, i) => (
              <Line
                key={name}
                type="monotone"
                dataKey={name}
                stroke={LINE_COLORS[i % LINE_COLORS.length]}
                strokeWidth={2}
                dot={{ r: 3 }}
                connectNulls
              />
            ))}
          </LineChart>
        </ResponsiveContainer>
      </div>
    </section>
  )
}