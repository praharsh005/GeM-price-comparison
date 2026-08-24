import { render, screen } from '@testing-library/react'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { describe, expect, it, vi } from 'vitest'

import ComparePage from '../pages/ComparePage'
import * as api from '../api'

vi.mock('../api', () => ({
  compareProduct: vi.fn(),
}))

function renderPage() {
  return render(
    <MemoryRouter initialEntries={['/compare/42']}>
      <Routes>
        <Route path="/compare/:id" element={<ComparePage />} />
      </Routes>
    </MemoryRouter>,
  )
}

const base = {
  id: 42,
  name: 'HP 15s Laptop',
  brand: 'HP',
  category: 'Laptops',
  match_confidence: null,
  market_average: 27440,
  last_updated: '2026-08-15T10:00:00Z',
  listings: [
    { id: 1, marketplace: { name: 'GeM' }, current_price: 28000, difference_from_gem: 0, availability: 'In Stock', scraped_at: '2026-08-15T10:00:00Z' },
    { id: 2, marketplace: { name: 'Flipkart' }, current_price: 27160, difference_from_gem: -840, availability: 'In Stock', scraped_at: '2026-08-15T10:00:00Z' },
  ],
  price_history: {},
}

describe('ComparePage', () => {
  it('shows a savings banner when GeM is cheaper than the market', async () => {
    api.compareProduct.mockResolvedValue({
      ...base,
      gem_price: 25000,
      market_best_price: 28000,
      savings: 3000,
      savings_pct: 10.7,
    })
    renderPage()

    await screen.findByRole('heading', { name: 'HP 15s Laptop' })
    expect(screen.getByText(/10.7% cheaper/)).toBeInTheDocument()
    expect(screen.getByText(/potential savings/)).toBeInTheDocument()
  })

  it('shows a costlier banner when GeM is more expensive than the market', async () => {
    api.compareProduct.mockResolvedValue({
      ...base,
      gem_price: 28000,
      market_best_price: 27160,
      savings: -840,
      savings_pct: -3,
    })
    renderPage()

    await screen.findByRole('heading', { name: 'HP 15s Laptop' })
    expect(screen.getByText(/3% costlier/)).toBeInTheDocument()
    expect(screen.getByText(/market offers/)).toBeInTheDocument()
  })

  it('renders the price trend chart when price history exists', async () => {
    api.compareProduct.mockResolvedValue({
      ...base,
      gem_price: 25000,
      market_best_price: 27160,
      price_history: {
        1: [
          { price: 25000, recorded_at: '2026-08-01T10:00:00Z' },
          { price: 24900, recorded_at: '2026-08-08T10:00:00Z' },
          { price: 25000, recorded_at: '2026-08-15T10:00:00Z' },
        ],
        2: [
          { price: 28000, recorded_at: '2026-08-01T10:00:00Z' },
          { price: 27160, recorded_at: '2026-08-15T10:00:00Z' },
        ],
      },
    })
    renderPage()

    await screen.findByRole('heading', { name: 'HP 15s Laptop' })
    expect(screen.getByRole('heading', { name: 'Price trend' })).toBeInTheDocument()
  })

  it('does not render the chart when there is no price history', async () => {
    api.compareProduct.mockResolvedValue({
      ...base,
      gem_price: 25000,
      market_best_price: 27160,
      price_history: {},
    })
    renderPage()

    await screen.findByRole('heading', { name: 'HP 15s Laptop' })
    expect(screen.queryByRole('heading', { name: 'Price trend' })).not.toBeInTheDocument()
  })
})
