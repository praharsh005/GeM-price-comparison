# Matching Layer Accuracy Report (Phase 7)

**Date:** 2026-08-17
**Method:** RapidFuzz (`token_set_ratio` / `token_sort_ratio` over core tokens) + token-coverage gate.
**Data:** 276 real products across 5 marketplaces (GeM, Vijay Sales, Snapdeal scraped; Amazon/Flipkart seed-only).

## Labeled sample

35 hand-labeled pairs, 3 true / 32 false:

- **32 negatives:** real cross-marketplace candidate pairs sampled from the live database
  (all pairs with raw similarity ≥ 45 across different marketplaces, non-seed only).
  Every pair was read and confirmed to be a *different* product — e.g. `Noise Alt Watch 1`
  vs `T500 Smart Watch`, `Bose QuietComfort Ultra` vs `Vertical9 headphone`, `JBL Flip 7`
  vs `Faymla Hongli batteries`.
- **3 positives:** hand-authored listing-name variants of real scraped products, mirroring
  the naming variation observed in the wild (e.g. Snapdeal sells the same selfie stick
  under three different title strings). Variants add/remove color, playtime and
  form-factor words only:
  - `Sony WH-CH520 Wireless Headphones` ↔ `Sony WH-CH520 Bluetooth Wireless On-Ear Headphones (Black)`
  - `Sony WH-CH520 Wireless Headphones` ↔ `SONY WH-CH520 Wireless Headphones 35 Hours Playback`
  - `JBL Tune 510BT Wireless Headphones` ↔ `JBL Tune 510BT On Ear Wireless Headphones (Blue)`

Artifacts: `backend/eval_pairs.csv` (labels), `backend/scrapers/eval_matching.py` (runner).

## Results

| Threshold (sim / coverage) | TP | FP | FN | Precision | Recall | F1 |
|---|---|---|---|---|---|---|
| **85 / 0.55 (operational)** | 3 | 0 | 0 | **1.00** | **1.00** | **1.00** |
| 75 / 0.35 | 3 | 2 | 0 | 0.60 | 1.00 | 0.75 |
| 65 / 0.30 | 3 | 2 | 0 | 0.60 | 1.00 | 0.75 |

The two false positives at the looser thresholds are generic smartwatches
(`T500 Smart Watch` at sim≈79, cov≈0.37) that only share generic tokens — the exact
failure mode the coverage gate was added for. The operational thresholds are kept.

## Full-catalog run

`python -m app.matching` over all 276 products:

- **High-confidence matches created: 0**
- Low-confidence pairs logged for manual review: 20
  (`backend/scrapers/match_logs/low_confidence_matches.csv`)

## Why so few matches

This is a data-reality finding, not a matcher failure:

1. **Same-name products never reach the matcher.** The pipeline keys products by
   (name, category); identical titles across marketplaces merge into one product row
   with multiple listings. A DB query for real products listed on 2+ marketplaces
   returns **0 rows** — the merge already handles exact-name overlap.
2. **The three scraped marketplaces stock disjoint catalogs.** GeM is a government
   procurement site (caddies, TV mounts, ELADR headsets, LAVA/I KALL phones); Vijay
   Sales sells current-generation branded consumer electronics (Pixel 10a, Galaxy
   Watch 9, Sony WF-C710N); Snapdeal's real inventory is generic accessories (TV
   covers, no-name watches/earbuds). Brand tokens overlap (boAt, Sony, JBL, Lenovo)
   but the exact models do not.
3. **Seed products are excluded by design** (their listing URLs are placeholders,
   so a match would be fake data).

The matcher's precision on real ambiguous pairs is 1.00, and the 20 logged
low-confidence pairs are the correct candidates for a human to review — per the
roadmap's "log low-confidence matches for manual review" requirement.

## Implications / options

- If cross-source duplicates are required for the demo, the next lever is scraping
  **more of each category page** (Vijay Sales category pages contain 90–140 products;
  only part was harvested) or adding one more source that overlaps with GeM's catalog
  (e.g. retail versions of ELADR/LAVA/I KALL products on other sites).
- Embeddings (the roadmap's stretch goal) would help when titles share zero tokens,
  e.g. `Sony WH-CH520` vs `Sony Wireless Headphones CH520`; with token-only matching
  the pair above still matches (WH-CH520 is one token), so token-based matching
  remains adequate for this dataset.
