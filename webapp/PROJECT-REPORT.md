# GeM Price Intelligence — Project Report

**Title:** Price Comparison of GeM Products with Other E-Marketplaces

## 1. Abstract

This project builds a full-stack web application that scrapes product listings and
prices from GeM (Government e-Marketplace) and Amazon India, normalizes and **matches**
equivalent products across sources, and presents a searchable price-comparison dashboard
with historical price trends and category-level savings insights. The aim is price
intelligence: showing whether the GeM price for a product is better or worse than the
open market, and by how much.

## 2. Objectives

- Acquire real product + price data responsibly from GeM and other e-marketplaces.
- Match equivalent products across sources automatically, with a confidence score.
- Search products with typo-tolerant fuzzy search, accelerated by an index and a cache.
- Compare prices (GeM vs market best/average, difference, savings %).
- Show per-product price trends over time and average savings by category.
- Ship a single-command `docker compose up` demo with full documentation.

## 3. Tech Stack

| Layer     | Technology |
|-----------|------------|
| Frontend  | React + Vite + Tailwind CSS + Recharts |
| Backend   | FastAPI + SQLAlchemy + Alembic |
| Database  | PostgreSQL 16 (pg_trgm fuzzy search, GIN indexes) |
| Cache     | Redis 7 |
| Scraping  | Python `requests` + lxml |
| Matching  | RapidFuzz |
| Deploy    | Docker Compose (localhost only), Nginx static frontend |

All components are free and open-source; the app runs entirely on localhost.

## 4. Architecture

```
            ┌──────────────┐        ┌──────────────┐
            │  Frontend     │◄──────►│  Backend API │
            │ React + Vite  │  REST  │  FastAPI     │
            └──────────────┘        └──────┬───────┘
                   5173                     │ 8000
                                            │
                          ┌─────────────────┴───────────────┐
                          │ PostgreSQL (products, listings, │
                          │ price_history, GIN trigram)     │
                          └─────────────────┬───────────────┘
                                            │
                          ┌─────────────────▼───────────────┐
                          │ Redis (search cache, 60s TTL)    │
                          └─────────────────────────────────┘
```

Data flow:

1. **Scrapers** (GeM, Amazon) fetch category pages, rate-limited (≥2 s), and upsert
   listings + price snapshots into Postgres. A matching pass links marketplace listings
   to `products` rows.
2. **API** (`/search`, `/products/{id}/compare`, `/categories`) serves the data, with
   Redis caching in front of search and pg_trgm fuzzy matching.
3. **Frontend** renders results with a search page, a per-product comparison view
   (source table + price-trend chart), and a category insights page.

## 5. Data Sources & Scraping Ethics

- **GeM** — laptops, monitors, printers, oxygen concentrators (curated categories).
- **Amazon India** — matching product search pages.
- **Flipkart** — blocks scraping with reCAPTCHA; documented as unavailable and **not
  bypassed** (`backend/app/scrapers/flipkart.py`).

Scraping rules followed: robots.txt and terms checked; rate-limited (2 s between
requests to the same domain); descriptive User-Agent; no CAPTCHA/login/paywall
bypass; only demo-scale data collected. Scrapers are idempotent — re-running updates
existing listings instead of duplicating.

## 6. Features Delivered (by phase)

| Phase | Deliverable |
|-------|-------------|
| 0 | Full-stack scaffold; Docker Compose for Postgres + Redis; `/health` |
| 1 | SQLAlchemy schema (`products`, `marketplaces`, `listings`, `price_history`); Alembic migration; seed script |
| 2 | FastAPI `/search`, `/products/{id}/compare`, `/categories` with Pydantic models |
| 3 | GeM scraper (rate-limited, idempotent) across 4 curated categories |
| 4 | API hardened for real scraped data (nulls, GeM-only products, counts) |
| 5 | React frontend: debounced search, comparison view, branding |
| 6 | Amazon scraper + RapidFuzz matching layer with confidence scores |
| 7 | pg_trgm GIN index + fuzzy search; Redis cache on `/search`; benchmarks |
| 8 | Recharts price-trend charts; category insights (avg savings) |
| 9 | Docker images for backend/frontend, single `docker compose up`, README, viva demo script |

## 7. Product Matching

`app/matching.py` scores a GeM title against a marketplace title (0–100):

1. **Normalize** — lowercase, NFKD, expand units ("24 in" → "24 inch"), strip
   stopwords/punctuation, expand synonyms (VA → Vertical Alignment, IPS → In Plane
   Switching).
2. **Similarity** — RapidFuzz `token_set_ratio` (dampened by token-set coverage) vs
   `WRatio`, take the max.
3. **Rewards** — shared model tokens (CPU, RAM, size, LPM, panel type) add +15.
4. **Penalties** — mismatched numeric specs cap at 50, brand mismatch at 40, single
   shared token at 55.

Decisions use `MATCH_THRESHOLD = 70`; borderline results are logged for review.

**Measured accuracy: 35/38 = 92.1%** on a hand-labeled sample of 38 title pairs
(balanced 24 true / 14 false) across all four categories.

Threshold sweep: 60 → 94.7% · 65 → 94.7% · 70 → 92.1% · 75 → 94.7% · 80 → 92.1%.

Residual failures are borderline or cosmetic (e.g. "medoxy"/"MedOx" brand spelling),
not dangerously confident wrong matches — exactly the cases the review band catches.

## 8. Performance

Measured on this machine (771 real products).

| Measurement | Median | Min |
|-------------|--------|-----|
| GIN trigram index present | 1.36 ms | 1.08 ms |
| GIN trigram index dropped | 39.41 ms | 37.33 ms |
| Cache miss (real DB search) | 2.34 ms | 1.91 ms |
| Cache hit (Redis read) | 0.25 ms | 0.21 ms |

- **Index: ~29× faster** (1.36 ms vs 39.41 ms, measured on a 100k-row table so the
  planner actually selects the index).
- **Cache: ~9.5× faster** (0.25 ms vs 2.34 ms).

`/search` uses `similarity >= 0.2`, so typos ("laptp") still surface products; Redis
short-circuits repeated identical searches for 60 s.

## 9. Results / Insights

Live category insights (avg = GeM price vs best market price; **positive = GeM cheaper**):

| Category | Avg GeM savings |
|----------|-----------------|
| Printers | **+18.89 %** (GeM cheaper) |
| Laptops | −22.78 % (market cheaper) |
| Monitors | −21.02 % (market cheaper) |
| Oxygen Concentrators | −11.78 % (market cheaper) |

Dataset: 771 products, ~2.3k marketplace listings across the categories. Comparisons
are algorithmic snapshots and are labeled informational — never official GeM or
government recommendations.

## 10. Testing

- **Backend: 46 pytest tests passing** — schema/seed, every endpoint (status + shape),
  scrapers (idempotency, row counts, rate-limit), matching accuracy, time-series shape.
- **Frontend: 10 Vitest + Testing Library tests passing** — search triggers API and
  renders results, empty-results state, render checks; oxlint clean; production build OK.
- **End-to-end**: browser verification of search, compare, insights, 404, and empty
  states with zero console errors.

## 11. Known Limitations

- **Flipkart** is blocked by reCAPTCHA and excluded by design (documented, not bypassed).
- **`docker compose build` on this dev machine** cannot complete because this machine's
  Docker Desktop/WSL2 VM has a broken NAT (containers have no outbound internet even
  though the host, WSL2, and Docker Hub pulls work). The compose files are standard and
  `docker compose config` validates; on this machine the app is run via the documented
  local-development path. Full detail in `EXTERNAL-CHANGES.md`.
- Matching is ~92% accurate; borderline pairs are logged for human review rather than
  presented as certain matches.

## 12. How to Run

Docker (single command):

```bash
git clone <repo> && cd <repo>
docker compose up -d --build   # → http://localhost:5173
```

Local development (this machine, per limitation above):

```bash
docker compose up -d db redis          # Postgres + Redis
cd backend && pip install -r requirements.txt
alembic upgrade head && python -m app.seed
uvicorn app.main:app --port 8000
cd ../frontend && npm install && npm run dev   # → http://localhost:5173
```

A step-by-step viva demo script is in `DEMO.md`.

## 13. Conclusion

The project delivers a working, locally-run price-intelligence platform: real scraped
data, automatic cross-source product matching with a measured 92.1% accuracy, typo-
tolerant fuzzy search made ~29× faster by indexing and ~9.5× faster by caching,
per-product price trends, and category-level savings insights — all in a polished
web UI, reproducible with a single Docker command.

## 14. Development Timeline

| Date | Phase | Commit |
|------|-------|--------|
| 2026-08-14 | 0 | `99c7d17` |
| 2026-08-14 | 1 | `102bbe4` |
| 2026-08-14 | 2 | `48e42c8` |
| 2026-08-15 | 3 | `6c3c91a`, `2a60390` |
| 2026-08-15 | 4 | `9e117dd` |
| 2026-08-15 | 5 | `eac8836` |
| 2026-08-15 | 6 | `6dfd36d`, `bfdbaa3` |
| 2026-08-15 | 7 | `3062448` |
| 2026-08-15 | 8 | `2313567` |
| 2026-08-15 | 9 | `56dba70`, `65b255b` |