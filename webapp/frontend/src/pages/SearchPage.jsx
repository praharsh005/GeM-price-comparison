import { useCallback, useEffect, useRef, useState } from 'react'
import { Link } from 'react-router-dom'
import {
  ArrowRight,
  Box,
  Camera,
  HardDrive,
  Headphones,
  Home,
  Laptop,
  Loader2,
  Monitor,
  Mouse,
  Printer,
  Refrigerator,
  Scissors,
  Search,
  Smartphone,
  Tag,
  Tv,
  Watch,
  Wind,
} from 'lucide-react'

import { listInsights, searchProducts } from '../api'
import ProductThumb from '../components/ProductThumb'
import { formatDate, formatINR, savingsLabel } from '../utils/format'

const CATEGORY_ICONS = {
  Appliances: Refrigerator,
  Audio: Headphones,
  Cameras: Camera,
  Grooming: Scissors,
  Home,
  Laptops: Laptop,
  'Mobile Phones': Smartphone,
  Monitors: Monitor,
  'Oxygen Concentrators': Wind,
  Peripherals: Mouse,
  Printers: Printer,
  Storage: HardDrive,
  Televisions: Tv,
  Wearables: Watch,
}

function useDebouncedSearch(delay = 400) {
  const [query, setQuery] = useState('')
  const [category, setCategory] = useState('')
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const timer = useRef(null)
  const seq = useRef(0)

  const trigger = useCallback(
    (q, cat) => {
      clearTimeout(timer.current)
      timer.current = setTimeout(async () => {
        const run = ++seq.current
        setLoading(true)
        setError(null)
        try {
          const data = await searchProducts({ q, category: cat, limit: 20 })
          if (run !== seq.current) return
          setResults(data)
        } catch {
          if (run !== seq.current) return
          setError('Search failed. Is the backend running?')
        } finally {
          if (run === seq.current) setLoading(false)
        }
      }, delay)
    },
    [delay],
  )

  const onQueryChange = (q) => {
    setQuery(q)
    trigger(q, category)
  }

  const onCategoryChange = (c) => {
    setCategory(c)
    trigger(query, c)
  }

  return { query, category, results, loading, error, onQueryChange, onCategoryChange }
}

function ResultCard({ item }) {
  const label = savingsLabel(item.savings_pct)
  const isGemCheaper = item.savings_pct > 0
  return (
    <li className="group flex flex-col gap-4 rounded-xl border border-[#D9E0E8] bg-white p-4 shadow-sm transition-shadow hover:shadow-md sm:flex-row sm:items-center">
      <Link to={`/compare/${item.id}`} className="shrink-0">
        <ProductThumb
          src={item.image_url}
          alt={item.name}
          className="h-16 w-16 rounded-lg border border-[#EEF2F6] sm:h-14 sm:w-14"
        />
      </Link>
      <div className="min-w-0 flex-1">
        <Link
          to={`/compare/${item.id}`}
          className="text-base font-semibold text-[#123B66] hover:underline"
        >
          {item.name}
        </Link>
        <div className="mt-1.5 flex flex-wrap items-center gap-x-3 gap-y-1 text-sm text-[#526071]">
          {item.brand && <span className="font-medium text-[#172033]">{item.brand}</span>}
          {item.category && (
            <span className="inline-flex items-center gap-1 rounded-md bg-[#F6F8FB] px-2 py-0.5 text-xs text-[#526071]">
              <Tag className="h-3 w-3" />
              {item.category}
            </span>
          )}
          {item.match_confidence != null && (
            <span className="rounded-md bg-[#EAF4EA] px-2 py-0.5 text-xs font-semibold text-[#15803D]">
              Match {Math.round(item.match_confidence)}%
            </span>
          )}
          <span className="text-xs text-[#718096]">Updated {formatDate(item.last_updated)}</span>
        </div>
      </div>
      <div className="flex items-end justify-between gap-6 sm:flex-col sm:items-end sm:gap-2 sm:min-w-[180px]">
        <div className="flex flex-col items-start sm:items-end">
          <span className="text-xs font-medium uppercase tracking-wide text-[#718096]">GeM Price</span>
          <span className="text-xl font-bold text-[#172033]">{formatINR(item.gem_price)}</span>
          {item.market_price != null && (
            <span className="text-xs text-[#718096]">Market from {formatINR(item.market_price)}</span>
          )}
        </div>
        <div className="flex flex-col items-start gap-1.5 sm:items-end">
          {label && (
            <span
              className={
                isGemCheaper
                  ? 'rounded-md bg-[#15803D]/10 px-2 py-0.5 text-sm font-semibold text-[#15803D]'
                  : 'rounded-md bg-[#B45309]/10 px-2 py-0.5 text-sm font-semibold text-[#B45309]'
              }
            >
              {isGemCheaper ? `${Math.abs(item.savings_pct)}% cheaper on GeM` : label}
            </span>
          )}
          <Link
            to={`/compare/${item.id}`}
            className="inline-flex items-center gap-1 text-sm font-semibold text-[#123B66] hover:underline"
          >
            View comparison <ArrowRight className="h-3.5 w-3.5" />
          </Link>
        </div>
      </div>
    </li>
  )
}

function CategoryBlock({ name, count, avg, active, onSelect }) {
  const Icon = CATEGORY_ICONS[name] || Box
  const hasAvg = avg !== null && avg !== undefined
  return (
    <button
      type="button"
      onClick={onSelect}
      aria-pressed={active}
      className={`flex flex-col items-start gap-1.5 rounded-xl border p-4 text-left transition ${
        active
          ? 'border-[#123B66] bg-[#123B66] text-white shadow-md'
          : 'border-[#D9E0E8] bg-white text-[#172033] hover:border-[#123B66]/40 hover:shadow-sm'
      }`}
    >
      <Icon className={`h-6 w-6 ${active ? 'text-[#F0C40A]' : 'text-[#123B66]'}`} />
      <span className="text-sm font-semibold">{name}</span>
      <span className={`text-xs ${active ? 'text-[#CBD5E1]' : 'text-[#718096]'}`}>
        {count} products
      </span>
      {hasAvg && (
        <span
          className={`text-xs font-semibold ${
            active ? 'text-[#F0C40A]' : avg > 0 ? 'text-[#15803D]' : 'text-[#B45309]'
          }`}
        >
          {avg > 0 ? 'GeM cheaper' : 'Market cheaper'}
        </span>
      )}
    </button>
  )
}

export default function SearchPage() {
  const { query, category, results, loading, error, onQueryChange, onCategoryChange } =
    useDebouncedSearch()
  const [categories, setCategories] = useState([])
  const resultsRef = useRef(null)

  useEffect(() => {
    let alive = true
    listInsights()
      .then((data) => alive && setCategories(data.categories ?? []))
      .catch(() => {})
    return () => {
      alive = false
    }
  }, [])

  const totalProducts = categories.reduce((sum, c) => sum + (c.products_with_gem || 0), 0)
  const showMetrics = totalProducts > 0

  const selectCategory = (name) => {
    onCategoryChange(category === name ? '' : name)
    resultsRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }

  return (
    <main>
      <section className="mx-auto max-w-6xl px-6 pt-8 sm:pt-12">
        <div className="rounded-2xl bg-[#F0C40A] px-6 py-10 sm:px-10 sm:py-14">
          <div className="mx-auto max-w-3xl text-center">
            <h1 className="text-3xl font-extrabold tracking-tight text-[#0B2743] sm:text-5xl">
              Find the better price before you buy.
            </h1>
            <p className="mt-3 text-base font-medium text-[#4A3B05] sm:text-lg">
              Compare GeM products with prices across major e-marketplaces and understand the
              difference.
            </p>

            <div className="relative mx-auto mt-8 max-w-xl">
              <Search className="pointer-events-none absolute left-4 top-1/2 h-5 w-5 -translate-y-1/2 text-[#718096]" />
              <input
                type="search"
                value={query}
                onChange={(e) => onQueryChange(e.target.value)}
                placeholder="Search products, e.g. laptop, monitor, oxygen"
                aria-label="Search products"
                className="w-full rounded-xl border-0 bg-white py-4 pl-12 pr-4 text-[#172033] shadow-lg outline-none focus:ring-4 focus:ring-[#0B2743]/20"
              />
            </div>

            {categories.length > 0 && (
              <div className="mt-5 flex flex-wrap items-center justify-center gap-2">
                {categories.map((c) => {
                  const active = category === c.category
                  return (
                    <button
                      key={c.category}
                      type="button"
                      onClick={() => onCategoryChange(active ? '' : c.category)}
                      className={
                        active
                          ? 'rounded-full bg-[#0B2743] px-3 py-1.5 text-sm font-medium text-white'
                          : 'rounded-full bg-white/70 px-3 py-1.5 text-sm font-medium text-[#0B2743] hover:bg-white'
                      }
                    >
                      {c.category}
                    </button>
                  )
                })}
              </div>
            )}
          </div>
        </div>
      </section>

      {showMetrics && (
        <section className="mx-auto max-w-6xl px-6 py-8" aria-label="Key metrics">
          <dl className="grid gap-4 sm:grid-cols-3">
            <div className="rounded-xl border border-[#D9E0E8] bg-white p-5 text-center">
              <dt className="text-sm text-[#718096]">Products analyzed</dt>
              <dd className="mt-1 text-3xl font-bold text-[#123B66]">
                {totalProducts.toLocaleString('en-IN')}
              </dd>
            </div>
            <div className="rounded-xl border border-[#D9E0E8] bg-white p-5 text-center">
              <dt className="text-sm text-[#718096]">Categories compared</dt>
              <dd className="mt-1 text-3xl font-bold text-[#123B66]">{categories.length}</dd>
            </div>
            <div className="rounded-xl border border-[#D9E0E8] bg-white p-5 text-center">
              <dt className="text-sm text-[#718096]">Marketplaces compared</dt>
              <dd className="mt-1 text-3xl font-bold text-[#123B66]">2</dd>
            </div>
          </dl>
        </section>
      )}

      <section className="mx-auto max-w-6xl px-6 pb-2" aria-label="Browse categories">
        <h2 className="text-xl font-bold tracking-tight text-[#172033]">Browse by category</h2>
        <div className="mt-4 grid grid-cols-2 gap-3 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-7">
          {categories.map((c) => (
            <CategoryBlock
              key={c.category}
              name={c.category}
              count={c.products_with_gem}
              avg={c.avg_savings}
              active={category === c.category}
              onSelect={() => selectCategory(c.category)}
            />
          ))}
        </div>
      </section>

      <section ref={resultsRef} className="mx-auto max-w-4xl px-6 pb-12">
        <div className="flex items-center justify-between text-sm text-[#526071]" role="status">
          {loading ? (
            <span className="inline-flex items-center gap-2">
              <Loader2 className="h-4 w-4 animate-spin" /> Searching…
            </span>
          ) : query ? (
            <span>
              {results.length} result{results.length === 1 ? '' : 's'}
            </span>
          ) : (
            <span>Start typing to search real GeM products.</span>
          )}
        </div>

        {error && <p className="mt-4 text-sm text-[#B91C1C]">{error}</p>}

        {!loading && !error && query && results.length === 0 && (
          <p className="mt-4 text-[#526071]">
            No products found for “{query}”. Try a different search term.
          </p>
        )}

        {results.length > 0 && (
          <ul className="mt-4 flex flex-col gap-3">
            {results.map((item) => (
              <ResultCard key={item.id} item={item} />
            ))}
          </ul>
        )}
      </section>
    </main>
  )
}