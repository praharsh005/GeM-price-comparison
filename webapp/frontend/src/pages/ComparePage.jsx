import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { ArrowLeft, BadgeCheck, Loader2, TrendingDown, TrendingUp } from 'lucide-react'

import { compareProduct } from '../api'
import PriceTrendChart from '../components/PriceTrendChart'
import ProductThumb from '../components/ProductThumb'
import { formatDate, formatINR } from '../utils/format'

function PriceCard({ label, value, accent, hint }) {
  return (
    <div className="rounded-xl border border-[#D9E0E8] bg-white p-5">
      <div className="text-xs font-medium uppercase tracking-wide text-[#718096]">{label}</div>
      <div className={`mt-1.5 text-2xl font-bold ${accent}`}>{formatINR(value)}</div>
      {hint && <div className="mt-1 text-xs text-[#718096]">{hint}</div>}
    </div>
  )
}

function ListingRow({ listing, isCheapest }) {
  const price = listing.price
  const diff = listing.difference_from_gem
  return (
    <tr className="border-b border-[#F6F8FB] last:border-0 hover:bg-[#F6F8FB]/60">
      <td className="py-3">
        <span className="font-semibold text-[#123B66]">{listing.marketplace_name}</span>
        {isCheapest && (
          <span className="ml-2 rounded bg-[#15803D]/10 px-2 py-0.5 text-xs font-semibold text-[#15803D]">
            Cheapest
          </span>
        )}
      </td>
      <td className="py-3 text-right font-semibold text-[#172033]">{formatINR(price)}</td>
      <td className="py-3 text-right text-sm text-[#526071]">
        {diff === null || diff === undefined
          ? '—'
          : diff === 0
            ? 'Baseline'
            : `${diff > 0 ? '+' : ''}${formatINR(diff)}`}
      </td>
      <td className="py-3 text-right text-sm text-[#718096]">
        {listing.availability ?? '—'}
      </td>
      <td className="py-3 text-right text-sm text-[#718096]">{formatDate(listing.scraped_at)}</td>
    </tr>
  )
}

export default function ComparePage() {
  const { id } = useParams()
  const [data, setData] = useState(null)
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let alive = true
    setLoading(true)
    setError(null)
    compareProduct(id)
      .then((d) => alive && setData(d))
      .catch(() => alive && setError('Unable to load this comparison.'))
      .finally(() => alive && setLoading(false))
    return () => {
      alive = false
    }
  }, [id])

  if (loading) {
    return (
      <main className="mx-auto flex max-w-5xl flex-col items-center px-6 py-16">
        <Loader2 className="h-6 w-6 animate-spin text-[#123B66]" role="status" aria-label="Loading comparison" />
      </main>
    )
  }

  if (error || !data) {
    return (
      <main className="mx-auto max-w-5xl px-6 py-16">
        <Link to="/" className="inline-flex items-center gap-1 text-sm text-[#123B66] hover:underline">
          <ArrowLeft className="h-4 w-4" /> Back to search
        </Link>
        <p className="mt-8 text-[#B91C1C]">{error ?? 'Product not found.'}</p>
      </main>
    )
  }

  const listings = data.listings ?? []
  const cheapestId = listings.reduce((bestIdx, l, i) => {
    if (l.price == null) return bestIdx
    if (bestIdx === null || l.price < listings[bestIdx].price) return i
    return bestIdx
  }, null)

  const gemCheaper = data.savings != null && data.savings > 0

  return (
    <main className="mx-auto max-w-5xl px-6 py-10">
      <Link to="/" className="inline-flex items-center gap-1 text-sm text-[#123B66] hover:underline">
        <ArrowLeft className="h-4 w-4" /> Back to search
      </Link>

      <header className="mt-6 flex items-start gap-4">
        <ProductThumb
          src={data.image_url}
          alt={data.name}
          className="h-20 w-20 shrink-0 rounded-xl border border-[#D9E0E8] sm:h-24 sm:w-24"
        />
        <div className="min-w-0">
          <h1 className="text-2xl font-bold tracking-tight text-[#172033] sm:text-3xl">
            {data.name}
          </h1>
          <div className="mt-2.5 flex flex-wrap items-center gap-x-4 gap-y-1.5 text-sm text-[#526071]">
          {data.brand && <span className="font-medium text-[#172033]">{data.brand}</span>}
          {data.category && (
            <span className="rounded-md bg-[#F6F8FB] px-2 py-0.5 text-xs text-[#526071]">
              {data.category}
            </span>
          )}
          {data.match_confidence != null && (
            <span className="inline-flex items-center gap-1 rounded-md bg-[#EAF4EA] px-2 py-0.5 text-xs font-semibold text-[#15803D]">
              <BadgeCheck className="h-3.5 w-3.5" />
              Match confidence {Math.round(data.match_confidence)}%
            </span>
          )}
          <span className="text-xs text-[#718096]">Updated {formatDate(data.last_updated)}</span>
        </div>
        </div>
      </header>

      <section className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <PriceCard label="GeM Price" value={data.gem_price} accent="text-[#123B66]" hint="Government e-Marketplace" />
        <PriceCard label="Market Best Price" value={data.market_best_price} accent="text-[#0F766E]" hint="Lowest comparable listing" />
        <PriceCard label="Market Average" value={data.market_average} accent="text-[#526071]" hint="Across comparable listings" />
        <PriceCard
          label="Potential Savings"
          value={data.savings != null ? Math.abs(data.savings) : null}
          accent={gemCheaper ? 'text-[#123B66]' : 'text-[#B45309]'}
          hint={gemCheaper ? 'Save on GeM vs market best' : 'Market best beats GeM'}
        />
      </section>

      {data.savings != null && gemCheaper && (
        <p className="mt-4 flex items-start gap-2 rounded-xl border border-[#F0C40A]/60 bg-[#F0C40A]/15 px-4 py-3 text-sm font-medium text-[#0B2743]">
          <TrendingDown className="mt-0.5 h-4 w-4 shrink-0" />
          GeM is {Math.abs(data.savings_pct)}% cheaper than the best market price — potential
          savings {formatINR(Math.abs(data.savings))}.
        </p>
      )}
      {data.savings != null && data.savings < 0 && (
        <p className="mt-4 flex items-start gap-2 rounded-xl border border-[#B45309]/30 bg-[#B45309]/5 px-4 py-3 text-sm font-medium text-[#B45309]">
          <TrendingUp className="mt-0.5 h-4 w-4 shrink-0" />
          GeM is {Math.abs(data.savings_pct)}% costlier than the best market price — the market
          offers {formatINR(Math.abs(data.savings))} less.
        </p>
      )}

      <section className="mt-8 overflow-x-auto rounded-xl border border-[#D9E0E8] bg-white shadow-sm">
        <table className="w-full min-w-[560px] text-sm">
          <thead>
            <tr className="border-b border-[#D9E0E8] bg-[#F6F8FB] text-left text-xs uppercase tracking-wide text-[#718096]">
              <th className="py-3 pl-4 font-semibold">Marketplace</th>
              <th className="py-3 text-right font-semibold">Price</th>
              <th className="py-3 text-right font-semibold">vs GeM</th>
              <th className="py-3 text-right font-semibold">Availability</th>
              <th className="py-3 pr-4 text-right font-semibold">Last updated</th>
            </tr>
          </thead>
          <tbody>
            {listings.map((l, i) => (
              <ListingRow key={l.id} listing={l} isCheapest={i === cheapestId} />
            ))}
          </tbody>
        </table>
      </section>

      <PriceTrendChart listings={listings} priceHistory={data.price_history} />

      <p className="mt-10 text-xs text-[#718096]">
        Prices are scraped snapshots and may be outdated. Comparisons are algorithmic and
        informational; not official recommendations.
      </p>
    </main>
  )
}