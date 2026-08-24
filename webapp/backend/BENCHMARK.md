# Search Performance Benchmark (Phase 7)

Measured on this machine (Windows, local Docker Postgres 16 + Redis 7)
with **771 real products** in the `products` table.

## Results

| Measurement | Median | Min |
|-------------|--------|-----|
| [1] GIN trigram index present | 1.36 ms | 1.08 ms |
| [2] GIN trigram index dropped | 39.41 ms | 37.33 ms |
| [3] Cache MISS (real DB search) | 2.34 ms | 1.91 ms |
| [4] Cache HIT (Redis read) | 0.25 ms | 0.21 ms |

**Speedups**
- Index: **~29x faster** with the GIN trigram index (1.36 ms vs 39.41 ms).
- Cache: **~9.5x faster** on a Redis cache hit (0.25 ms vs 2.34 ms).

## Method

`scripts/benchmark_search.py` (run `python scripts/benchmark_search.py`):

1. **Index comparison** runs a selective `ILIKE '%…%'` + `ORDER BY
   similarity(...)` query against a throwaway **100k-row table** — 771 real
   products are too few for the planner to choose the index, so a temp table
   makes the before/after difference real. The query matches ~100 rows in
   100k. With the index: bitmap index scan. Without it: seq scan.
2. **Cache comparison** times the real DB search query (miss) vs a Redis
   `GET` (hit) at a 120s TTL.

Median of 30 (index) / 200 (cache) iterations. The script asserts both
speedups are positive and exits non-zero otherwise.

## Why it matters

- `/search` now uses `pg_trgm` fuzzy matching (`similarity >= 0.2`) so
  typos ("laptp") still surface products — verified against the live API.
- Redis caching short-circuits repeated identical searches for 60s,
  removing the DB round-trip on cache hits.
- The GIN index keeps fuzzy/substring search fast as the product catalog
  grows well beyond the current 771 rows.

## Re-running

```bash
cd backend
python scripts/benchmark_search.py
```