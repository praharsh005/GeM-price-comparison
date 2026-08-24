# Product Matching (Phase 6)

The matching layer links listings from different marketplaces (GeM, Amazon)
that describe the same product into a single `products` row, and records a
match-confidence score on each non-GeM `Listing`.

## How it works

`app/matching.py` scores a GeM title against a marketplace title and returns
0–100 confidence:

1. **Normalize** — lowercase, NFKD, expand "24 in" → "24 inch", strip
   punctuation/stopwords, expand synonyms (Vertical Alignment → VA,
   In Plane Switching → IPS).
2. **Similarity** — RapidFuzz `token_set_ratio` (dampened by token-set
   coverage) vs `WRatio`, take the max.
3. **Rewards** — shared model tokens (CPU model, RAM, size, LPM, panel type)
   add +15.
4. **Penalties** — mismatched numeric capacities/sizes cap at 50; a known
   brand mismatch caps at 40; a single shared token caps at 55.

Decisions use `MATCH_THRESHOLD = 70` (accept) and
`REVIEW_THRESHOLD = 85` (high vs medium). Accepted matches below 85 and all
rejected candidates are logged via `log_review` for manual review.

## Measured accuracy

The matcher is scored against `tests/matching_sample.py`, a hand-labeled
sample of 38 title pairs across all four categories (Laptops, Monitors,
Printers, Oxygen Concentrators), balanced 24 true / 14 false.

**Accuracy: 35/38 = 92.1%** at `MATCH_THRESHOLD = 70`.

Threshold sweep on the sample:

| Threshold | Accuracy |
|-----------|----------|
| 60        | 94.7%    |
| 65        | 94.7%    |
| 70        | 92.1%    |
| 75        | 94.7%    |
| 80        | 92.1%    |

## Why the 3 misses fail

All three remaining errors sit in the review band or are cosmetic aliases;
none is a dangerously confident wrong match:

1. **Canon PIXMA G2370** (predicted match 73.1, labeled non-match) — a
   borderline false positive: A4 colour inkjet Canon titles share every
   attribute except the model string, which GeM does not carry.
2. **Canon imageCLASS LBP225dn** (predicted 68.2, labeled match) — the
   mirror image of (1): a genuine A4 mono laser match scoring just under
   the threshold because the model token is missing from the GeM title.
3. **medoxy / MedOx** (predicted 55, labeled match) — the same brand
   spelled two ways (word-boundary tokens differ), so it falls under the
   thin-overlap cap.

These are exactly the cases `REVIEW_THRESHOLD` exists for: the outcomes are
logged, and a human can confirm before the pair is presented as equivalent.

## Re-running

```bash
cd backend
python -m pytest tests/test_matching.py -q   # accuracy + unit tests
python -m app.scrapers.amazon --pages 1       # live scrape + matching
```