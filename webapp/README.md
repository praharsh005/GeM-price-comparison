# GeM Price Intelligence

Compare GeM (Government e-Marketplace) product prices with relevant listings from other
e-marketplaces (Amazon, Flipkart), normalize and match equivalent products, and present the
results as searchable price comparisons with historical trends and category-level savings
insights.

**Compare. Understand. Save.**

This is a non-commercial academic project. All comparisons are algorithmic and informational;
nothing here is an official GeM or government recommendation.

---

## What it does

- Scrapes product listings and prices from **GeM** and **Amazon India** (Flipkart is
  documented-blocked by reCAPTCHA and is not bypassed).
- **Matches** equivalent products across sources with a RapidFuzz-based matcher and a
  per-match confidence score (`backend/MATCHING.md`).
- **Searches** products with fuzzy, indexed search plus a Redis cache layer
  (`backend/BENCHMARK.md`).
- **Compares** prices per product: GeM price vs market best/average, price difference and
  savings %, source table, and a Recharts **price-trend chart** from stored price history.
- **Insights** page: average GeM savings by category.

## Tech stack

| Layer     | Technology |
|-----------|------------|
| Frontend  | React + Vite + Tailwind CSS + Recharts (shadcn/ui-style components) |
| Backend   | FastAPI + SQLAlchemy + Alembic |
| Database  | PostgreSQL 16 |
| Cache     | Redis 7 |
| Scraping  | Python `requests` + lxml (respects robots.txt, rate-limited) |
| Matching  | RapidFuzz |
| Deploy    | Docker Compose (localhost only) |

---

## Quick start (Docker Compose — recommended)

Requirements: **Docker** with Docker Compose v2. No local Python/Node needed.

```bash
git clone https://github.com/praharsh005/GeM-Price-Intelligence.git
cd GeM-Price-Intelligence
docker compose up -d --build
```

This starts four containers:

| Container | URL |
|-----------|-----|
| Frontend  | http://localhost:5173 |
| Backend API | http://localhost:8000 (docs: http://localhost:8000/docs) |
| PostgreSQL | localhost:5432 (gem/gem, db `gem_price`) |
| Redis | localhost:6379 |

On first start the backend container:
1. waits for Postgres,
2. runs `alembic upgrade head` (applies migrations),
3. seeds the database with 20 demo products across 3 marketplaces (only if empty),
4. starts the API.

Open **http://localhost:5173** and search for e.g. `laptop`, `monitor`, `printer`, or `oxygen`.

To see logs:

```bash
docker compose logs -f backend
```

To stop:

```bash
docker compose down
```

To also remove the database volume (reset to fresh seed):

```bash
docker compose down -v
```

### Troubleshooting

- **`docker compose build` fails with `Network is unreachable` (pip/npm in build containers).**
  Build containers need outbound internet to fetch dependencies. On some Windows +
  Docker Desktop + WSL2 setups the Docker VM's NAT is broken (iptables/nftables missing
  from the VM filesystem), so containers cannot reach the internet even though the host,
  WSL2, and Docker Hub pulls all work. On such a machine, run the app via the
  [local development](#local-development-without-docker) path instead.
- **Backend tests fail with SQLAlchemy `OperationalError`.** The tests need Postgres; start
  the database first: `docker compose up -d db`.

---

## Local development (without Docker)

### 1. Backend

Requires Python 3.11+.

```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate   |  macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Start Postgres + Redis (via Docker, optional):

```bash
docker compose up -d db redis
```

Run migrations and seed:

```bash
cd backend
alembic upgrade head
python -m app.seed
```

Start the API:

```bash
uvicorn app.main:app --reload
# → http://localhost:8000/docs
```

### 2. Frontend

Requires Node 18+.

```bash
cd frontend
npm install
npm run dev
# → http://localhost:5173
```

The Vite dev server proxies `/search`, `/products`, `/categories`, `/health` to the backend
on port 8000 (see `frontend/vite.config.js`).

### Optional: run the live scrapers

```bash
cd backend
python -m app.scrapers.gem --pages 2        # GeM categories
python -m app.scrapers.amazon --pages 2     # Amazon India
```

Scrapers are rate-limited (default 2s between requests) and idempotent (re-running updates
existing listings instead of duplicating). See `backend/app/scrapers/` and the scraping
ethics section below.

---

## API endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| GET | `/search?q=&category=&limit=` | Fuzzy product search with per-product GeM vs market price + savings + match confidence (cached in Redis, 60s TTL) |
| GET | `/products/{id}/compare` | Full comparison: all listings vs GeM, price difference/%, market average, match confidence, per-listing price history |
| GET | `/categories` | Category list with product counts and average GeM savings % (positive = GeM cheaper) |

Interactive docs: `http://localhost:8000/docs`.

---

## Tests

Backend (pytest):

```bash
cd backend
pytest
```

Frontend (Vitest + Testing Library) and lint/build:

```bash
cd frontend
npm test
npm run lint
npm run build
```

---

## Key measurement results (for the project report)

- **Product-matching accuracy: 92.1%** (35/38) on a hand-labeled sample of 38 product pairs
  at the `MATCH_THRESHOLD = 70` cutoff. Details and residual failure analysis:
  `backend/MATCHING.md`.
- **Search with pg_trgm GIN index: ~29x faster** (1.36 ms vs 39.41 ms on a 100k-row table).
- **Redis search cache: ~9.5x faster** (0.25 ms vs 2.34 ms).
  Details: `backend/BENCHMARK.md`.

## Scraping ethics

- `robots.txt` and site terms are checked before scraping.
- Requests are rate-limited (default 2 s between requests to the same domain).
- An honest, descriptive User-Agent is used.
- CAPTCHAs, logins, paywalls, and anti-bot controls are never bypassed. Flipkart blocks
  scraping via reCAPTCHA, so that source is documented as unavailable rather than forced
  (`backend/app/scrapers/flipkart.py`).
- Only what is needed for the demo dataset is scraped — no full-site crawls.

## Repository layout

```
backend/
  app/
    main.py            FastAPI app
    routes.py          /search, /products/{id}/compare, /categories
    models.py          products, marketplaces, listings, price_history
    matching.py        RapidFuzz product matcher
    scrapers/          gem.py, amazon.py, flipkart.py (blocked, documented)
    seed.py            demo data
  alembic/             migrations
  tests/               pytest suite
  scripts/             benchmark_search.py
  MATCHING.md, BENCHMARK.md
frontend/
  src/
    pages/             SearchPage, ComparePage, InsightsPage
    components/        PriceTrendChart
    App.jsx            routes + layout
  Dockerfile, nginx.conf
docker-compose.yml     db + redis + backend + frontend
DESIGN.md              design system (authoritative for UI)
DEMO.md                scripted demo flow for the viva
```

---

## Demo script

A step-by-step demo flow for presentations/viva is in **`DEMO.md`**.

---

## Design system

UI follows `DESIGN.md` (colors, typography, spacing, accessibility, brand logo usage).
Product name: **GeM Price Intelligence**.