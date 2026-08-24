"""Phase 8 benchmark: /search latency with/without cache and trigram index.

Usage (from backend/):  venv\\Scripts\\python.exe -X utf8 scripts\\benchmark_search.py
Requires: uvicorn running on :8000 (python -m uvicorn app.main:app --port 8000),
Redis up (docker compose up -d), and one warm request per query beforehand.
"""
import statistics
import time
import urllib.parse
import urllib.request

BASE = "http://127.0.0.1:8000"
QUERIES = [
    "smartwatch",
    "laptop",
    "earbuds",
    "television",
    "headphone",
    "iphone",
    "caddy",
    "samsung",
]
N_RUNS = 20


def fetch(path: str) -> tuple[float, int]:
    start = time.perf_counter()
    with urllib.request.urlopen(f"{BASE}{path}", timeout=30) as resp:
        resp.read()
    return (time.perf_counter() - start) * 1000, resp.status


def warm(path: str) -> None:
    try:
        fetch(path)
    except Exception:  # noqa: BLE001
        pass


def bench(label: str, path: str) -> dict:
    latencies = []
    for _ in range(N_RUNS):
        ms, status = fetch(path)
        latencies.append(ms)
    latencies.sort()
    return {
        "label": label,
        "p50": round(statistics.median(latencies), 2),
        "p95": round(latencies[int(0.95 * (N_RUNS - 1))], 2),
        "mean": round(statistics.mean(latencies), 2),
    }


def main() -> None:
    results = []

    for q in QUERIES:
        path = f"/search?q={urllib.parse.quote(q)}"
        warm(path)
        warm(path)
        cached = bench(f"cached  q={q}", path)
        time.sleep(31)
        cold = bench(f"db+idx  q={q}", path)
        results.append((cold, cached))
        print(f"{cached['label']:>22}: p50 {cached['p50']:>8.2f} ms  p95 {cached['p95']:>8.2f} ms")
        print(f"{cold['label']:>22}: p50 {cold['p50']:>8.2f} ms  p95 {cold['p95']:>8.2f} ms")
        print()

    for q in QUERIES[:2]:
        path = f"/search?q={urllib.parse.quote(q)}&category=wearables"
        warm(path)
        warm(path)
        cached = bench(f"cached  cat+{q}", path)
        time.sleep(31)
        cold = bench(f"db+idx  cat+{q}", path)
        results.append((cold, cached))
        print(f"{cached['label']:>22}: p50 {cached['p50']:>8.2f} ms  p95 {cached['p95']:>8.2f} ms")
        print(f"{cold['label']:>22}: p50 {cold['p50']:>8.2f} ms  p95 {cold['p95']:>8.2f} ms")
        print()

    speedups = [
        (c["p50"] / c2["p50"]) if c2["p50"] else float("inf")
        for c, c2 in results
    ]
    avg_speedup = statistics.mean(speedups)
    print(f"avg p50 speedup from cache: {avg_speedup:.1f}x")
    print(f"cold p50 range: {min(c['p50'] for c, _ in results):.2f}-{max(c['p50'] for c, _ in results):.2f} ms")
    print(f"cached p50 range: {min(c2['p50'] for _, c2 in results):.2f}-{max(c2['p50'] for _, c2 in results):.2f} ms")


if __name__ == "__main__":
    main()