# GeM Price Intelligence — Frontend

React + Vite + Tailwind CSS + Recharts frontend for the GeM price-comparison platform.

Full setup instructions are in the repository **`README.md`** (root). Dev-mode summary:

```bash
npm install
npm run dev        # → http://localhost:5173 (proxies /search, /products, /categories to :8000)
npm test           # Vitest
npm run lint       # oxlint
npm run build      # production build (served via nginx in Docker)
```

## Layout

- `src/pages/SearchPage.jsx` — debounced fuzzy search
- `src/pages/ComparePage.jsx` — per-product comparison + price trend chart
- `src/pages/InsightsPage.jsx` — average GeM savings by category
- `src/components/PriceTrendChart.jsx` — Recharts multi-marketplace line chart
- `src/App.jsx` — routes (`/`, `/compare/:id`, `/insights`) and layout

UI follows `DESIGN.md` (root).