import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import SearchPage from '../pages/SearchPage'
import * as api from '../api'

vi.mock('../api', () => ({
  searchProducts: vi.fn(),
  listCategories: vi.fn(),
}))

const sampleResults = [
  {
    id: 42,
    name: 'hp Intel Core i5 1245U Mid Level Laptop Notebook',
    brand: 'hp',
    category: 'Laptops',
    gem_price: 25000,
    market_price: 22000,
    savings: 3000,
    savings_pct: 12.0,
    last_updated: '2026-08-15T10:00:00Z',
  },
]

function renderPage() {
  return render(
    <MemoryRouter>
      <SearchPage />
    </MemoryRouter>,
  )
}

beforeEach(() => {
  api.listCategories.mockResolvedValue([
    { name: 'Laptops', product_count: 120, avg_savings: 4.2 },
  ])
})

describe('SearchPage', () => {
  it('triggers the search API call when the user types (debounced)', async () => {
    api.searchProducts.mockResolvedValue(sampleResults)
    const user = userEvent.setup()
    renderPage()

    const input = screen.getByRole('searchbox', { name: /search products/i })
    await user.type(input, 'hp')

    await waitFor(() => {
      expect(api.searchProducts).toHaveBeenCalledTimes(1)
      expect(api.searchProducts).toHaveBeenCalledWith(expect.objectContaining({ q: 'hp' }))
    })
  })

  it('renders search results returned by the API', async () => {
    api.searchProducts.mockResolvedValue(sampleResults)
    const user = userEvent.setup()
    renderPage()

    await user.type(screen.getByRole('searchbox', { name: /search products/i }), 'hp')

    await screen.findByText('hp Intel Core i5 1245U Mid Level Laptop Notebook')
    expect(screen.getByText(/25,000/)).toBeInTheDocument()
    expect(screen.getByText(/12% cheaper/)).toBeInTheDocument()
    expect(screen.getByText(/1 result/)).toBeInTheDocument()
  })

  it('shows an empty-results message when a query returns nothing', async () => {
    api.searchProducts.mockResolvedValue([])
    const user = userEvent.setup()
    renderPage()

    await user.type(screen.getByRole('searchbox', { name: /search products/i }), 'zzz')

    await screen.findByText(/No products found/)
    expect(screen.getByText(/zzz/)).toBeInTheDocument()
  })
})