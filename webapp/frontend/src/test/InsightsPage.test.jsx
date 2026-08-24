import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { describe, expect, it, vi } from 'vitest'

import InsightsPage from '../pages/InsightsPage'
import * as api from '../api'

vi.mock('../api', () => ({
  listCategories: vi.fn(),
}))

function renderPage() {
  return render(
    <MemoryRouter>
      <InsightsPage />
    </MemoryRouter>,
  )
}

const categories = [
  { name: 'Laptops', product_count: 120, avg_savings: 4.2 },
  { name: 'Monitors', product_count: 60, avg_savings: -2.1 },
  { name: 'Printers', product_count: 40, avg_savings: null },
]

describe('InsightsPage', () => {
  it('renders category insight cards with savings direction', async () => {
    api.listCategories.mockResolvedValue({ total: 3, categories })
    renderPage()

    expect(await screen.findByRole('heading', { name: 'Category insights' })).toBeInTheDocument()
    expect(screen.getByText(/120 products/)).toBeInTheDocument()
    expect(screen.getByText(/4.2% cheaper on GeM/)).toBeInTheDocument()
    expect(screen.getByText(/2.1% costlier on GeM/)).toBeInTheDocument()
    expect(screen.getByText(/No market prices to compare yet/)).toBeInTheDocument()
  })

  it('shows an error when the backend is unreachable', async () => {
    api.listCategories.mockRejectedValue(new Error('boom'))
    renderPage()

    expect(await screen.findByText(/Unable to load insights/)).toBeInTheDocument()
  })

  it('renders the average savings bar chart when data exists', async () => {
    api.listCategories.mockResolvedValue({ total: 3, categories })
    renderPage()

    await screen.findByRole('heading', { name: 'Category insights' })
    expect(screen.getByRole('heading', { name: 'Average savings by category' })).toBeInTheDocument()
  })
})