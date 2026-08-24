"""Phase 7 benchmark: measure /search latency with/without Redis cache and
with/without the GIN trigram index.

Run from the backend dir:
    python scripts/benchmark_search.py

The index comparison runs against a throwaway 100k-row table (771 real
products are too few for the planner to choose the index). The cache
comparison measures the real DB search (miss) vs a Redis read (hit).

Prints before/after numbers for the project report and exits non-zero if
no measurable improvement is observed.
"""

import statistics
import time

from sqlalchemy import create_engine, text

from app.cache import SEARCH_PREFIX, clear_search_cache, get_json, set_json
from app.config import settings

QUERIES = 30
CACHE_TTL = 120

INDEX_NAME = "ix_bench_name_trgm"
TABLE_NAME = "bench_products_ph7"

INDEX_QUERY = (
    f"SELECT name FROM {TABLE_NAME} "
    "WHERE name ILIKE '%Model 50000%' ORDER BY similarity(name, 'Model 50000') DESC LIMIT 20"
)
SEARCH_QUERY = (
    "SELECT name FROM products WHERE name ILIKE '%laptop%' "
    "ORDER BY similarity(name, 'laptop') DESC LIMIT 20"
)


def _time_call(fn, n=QUERIES):
    samples = []
    for _ in range(n):
        start = time.perf_counter()
        fn()
        samples.append(time.perf_counter() - start)
    return statistics.median(samples) * 1000, min(samples) * 1000


def _db(engine, sql):
    with engine.connect() as conn:
        conn.execute(text(sql)).fetchall()


def main():
    engine = create_engine(settings.database_url)

    with engine.begin() as conn:
        conn.execute(text(f"DROP TABLE IF EXISTS {TABLE_NAME}"))
        conn.execute(text(f"CREATE TABLE {TABLE_NAME} (id int, name text)"))
        conn.execute(
            text(
                f"INSERT INTO {TABLE_NAME} "
                "SELECT g, 'Brand Model ' || lpad(g::text, 6, '0') || ' Series ' || (g % 20) "
                "FROM generate_series(1, 100000) g"
            )
        )
        conn.execute(text(f"INSERT INTO {TABLE_NAME} VALUES (0, 'Generic Ultrabook Laptop')"))
        conn.execute(text(f"CREATE INDEX {INDEX_NAME} ON {TABLE_NAME} USING gin (name gin_trgm_ops)"))
        conn.execute(text(f"ANALYZE {TABLE_NAME}"))

    with_ix, with_ix_min = _time_call(lambda: _db(engine, INDEX_QUERY))
    print(f"[1] GIN trigram index present:   median {with_ix:.2f} ms, min {with_ix_min:.2f} ms")

    with engine.begin() as conn:
        conn.execute(text(f"DROP INDEX IF EXISTS {INDEX_NAME}"))
        conn.execute(text(f"ANALYZE {TABLE_NAME}"))
    try:
        without_ix, without_ix_min = _time_call(lambda: _db(engine, INDEX_QUERY))
        print(f"[2] GIN trigram index dropped:   median {without_ix:.2f} ms, min {without_ix_min:.2f} ms")
    finally:
        with engine.begin() as conn:
            conn.execute(text(f"DROP TABLE IF EXISTS {TABLE_NAME}"))

    # --- cache miss (real DB search) vs cache hit (Redis read) ---
    key = f"{SEARCH_PREFIX}benchmark:laptop:20"
    clear_search_cache()

    cache_miss, cache_miss_min = _time_call(lambda: _db(engine, SEARCH_QUERY))
    print(f"[3] Cache MISS (real DB search):  median {cache_miss:.2f} ms, min {cache_miss_min:.2f} ms")

    set_json(key, {"bench": 1}, ttl=CACHE_TTL)
    cache_hit, cache_hit_min = _time_call(lambda: get_json(key), n=200)
    print(f"[4] Cache HIT (Redis read):       median {cache_hit:.2f} ms, min {cache_hit_min:.2f} ms")
    clear_search_cache()

    print()
    if without_ix > 0:
        print(f"index speedup: {without_ix / with_ix:.1f}x faster with index")
    if cache_hit > 0:
        print(f"cache speedup: {cache_miss / cache_hit:.1f}x faster on hit")

    ok = with_ix < without_ix and cache_hit < cache_miss
    print("RESULT:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())