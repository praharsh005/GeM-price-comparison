# DEMO.md — Scripted demo flow (viva)

This is a 5-minute walkthrough. Everything below works from a **fresh clone** using only the
commands in `README.md`. The screens you'll show use the **seeded demo data** (20 products
across 3 marketplaces with price history), which is what a fresh `docker compose up` produces.

---

## 0. Before you start

```bash
git clone <this-repo>
cd <repo>
docker compose up -d --build
```

Wait for the backend to finish migrations + seeding (first build takes a few minutes):

```bash
docker compose logs -f backend
```

Stop following logs when you see:

```
Seeded: {'marketplaces': 3, 'products': 20, 'listings': 60, 'price_history': 120}
Uvicorn running on http://0.0.0.0:8000
```

Confirm everything is up:

| Check | Command | Expect |
|-------|---------|--------|
| API health | `curl http://localhost:8000/health` | `{"status":"ok",...}` |
| Frontend | open `http://localhost:5173` | Homepage with search bar |

---

## 1. Search (30 seconds)

1. On the homepage type **`laptop`** in the search box.
2. Results appear **without pressing Enter** (debounced search) with a brief "Searching…"
   spinner.
3. Point out the per-result card shows: **GeM Price**, **Market from ₹…**, a **Match %**
   badge (e.g. `Match 86%`), brand/category, and last updated.
4. Mention the backend is doing **fuzzy, typo-tolerant search** — try `laptp` to prove it.

## 2. Comparison view (60 seconds)

1. Click any laptop result, e.g. **HP 15s Laptop**.
2. Explain the three summary cards: **GeM Price**, **Market Best Price**, **Market Average**.
3. Point out the savings/costlier banner ("GeM is X% cheaper than the best market price —
   potential savings ₹Y").
4. Scroll to the **marketplace table**: source, price, *vs GeM* column, availability, last
   updated, and the green **Cheapest** badge.
5. Scroll to the **Price trend** line chart — one line per marketplace from stored
   `price_history`, showing prices over time. This is the Phase 8 deliverable.
6. Note the **Match confidence** in the header and the disclaimer at the bottom.

## 3. Insights page (45 seconds)

1. Click **Insights** in the header.
2. Explain the category cards: product count + *"Avg X% cheaper/costlier on GeM"*.
3. Explain the **Average savings by category** bar chart (positive = GeM cheaper).
4. Caveat: this is algorithmic price intelligence, not an official recommendation.

## 4. Engineering talking points (if asked)

- **Stack:** FastAPI + SQLAlchemy/Alembic, PostgreSQL, Redis, React/Vite/Tailwind/Recharts,
  Docker Compose.
- **Scraping ethics:** robots.txt respected, 2s rate limit, honest UA, no CAPTCHA bypass.
  Flipkart is documented-blocked (`app/scrapers/flipkart.py`) rather than forced.
- **Matching accuracy: 92.1%** on 38 hand-labeled pairs (`backend/MATCHING.md`). Show the
  doc if asked.
- **Search performance:** pg_trgm GIN index ≈ 29× speedup; Redis cache ≈ 9.5× speedup
  (`backend/BENCHMARK.md`).
- **Endpoints:** `/search`, `/products/{id}/compare`, `/categories`; Swagger at
  `http://localhost:8000/docs`.

## 5. Optional live-scrape extension (if the room has internet)

```bash
docker compose exec backend python -m app.scrapers.gem --pages 1
docker compose exec backend python -m app.scrapers.amazon --pages 1
```

Rate-limited and idempotent (updates listings, no duplicates). Re-search the same term to
show fresh data timestamps. Do **not** rely on live scraping during the demo — it depends on
network and the target sites.

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `backend` container exits | `docker compose logs backend` — Postgres needs to be healthy first; the entrypoint retries for ~60s |
| Frontend can't reach API | Confirm `backend` is running (`docker compose ps`); nginx proxies `/search`, `/products`, `/categories`, `/health` to `backend:8000` |
| Database has scraped data you want to keep | Do **not** run `docker compose down -v` (that wipes the volume); seed only runs when the DB is empty |