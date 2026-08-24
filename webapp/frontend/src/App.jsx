import { BrowserRouter, Link, NavLink, Route, Routes } from 'react-router-dom'

import ComparePage from './pages/ComparePage'
import InsightsPage from './pages/InsightsPage'
import SearchPage from './pages/SearchPage'

function navClass({ isActive }) {
  return `rounded-lg px-3 py-1.5 text-sm font-medium transition-colors ${
    isActive ? 'bg-white/10 text-white' : 'text-[#A7B0BE] hover:bg-white/5 hover:text-white'
  }`
}

function Layout({ children }) {
  return (
    <div className="min-h-screen bg-[#F6F8FB] text-[#172033]">
      <header className="border-b border-[#0B2743] bg-[#1F2430]">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-3">
          <Link to="/" className="flex items-center gap-3" aria-label="GeM Price Intelligence home">
            <img
              src="/brand-logo.png"
              alt="GeM Price Intelligence logo"
              className="h-9 w-9 rounded-md object-cover invert"
            />
            <span className="text-lg font-semibold text-white">GeM Price Intelligence</span>
          </Link>
          <nav className="flex items-center gap-2">
            <NavLink to="/" end className={navClass}>
              Compare
            </NavLink>
            <NavLink to="/insights" className={navClass}>
              Insights
            </NavLink>
          </nav>
        </div>
      </header>
      {children}
      <footer className="border-t border-[#D9E0E8] py-6 text-center text-xs text-[#718096]">
        Prices are scraped snapshots and may change. Informational use only.
      </footer>
    </div>
  )
}

function NotFound() {
  return (
    <main className="mx-auto max-w-4xl px-6 py-16 text-center">
      <h1 className="text-2xl font-bold text-[#172033]">Page not found</h1>
      <p className="mt-2 text-[#526071]">The page you’re looking for doesn’t exist.</p>
      <Link
        to="/"
        className="mt-6 inline-block rounded-lg bg-[#123B66] px-4 py-2 text-sm font-medium text-white hover:bg-[#0E2E4F]"
      >
        Back to search
      </Link>
    </main>
  )
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout><SearchPage /></Layout>} />
        <Route path="/compare/:id" element={<Layout><ComparePage /></Layout>} />
        <Route path="/insights" element={<Layout><InsightsPage /></Layout>} />
        <Route path="*" element={<Layout><NotFound /></Layout>} />
      </Routes>
    </BrowserRouter>
  )
}

export default App