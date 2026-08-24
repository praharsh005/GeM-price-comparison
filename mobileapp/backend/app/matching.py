import csv
import re
from datetime import datetime, timezone
from pathlib import Path

from rapidfuzz import fuzz
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Listing, Marketplace, Product, ProductMatch

HIGH_THRESHOLD = 85.0
LOW_THRESHOLD = 55.0
MIN_COVERAGE = 0.55
LOW_COVERAGE = 0.30
LOG_DIR = Path(__file__).resolve().parent.parent / "scrapers" / "match_logs"


def normalize_name(name: str) -> str:
    text = name.lower()
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def _token_sets(normalized: str) -> tuple[set[str], set[str]]:
    tokens = set(normalized.split())
    generic = {
        "tv", "led", "lcd", "oled", "qled", "hd", "fhd", "uhd", "4k", "8k",
        "smart", "google", "android", "smartphone", "mobile", "phone",
        "laptop", "cm", "inch", "inches", "in", "mm", "gb", "tb", "ram",
        "bluetooth", "wireless", "wifi", "series", "model", "with", "for",
        "and", "the", "new", "plus", "pro", "5g", "amazon", "sale", "offer",
    }
    return tokens - generic, tokens


def _is_seed_product(db: Session, product_id: int) -> bool:
    return (
        db.execute(
            select(Listing.id)
            .join(Marketplace, Marketplace.id == Listing.marketplace_id)
            .where(Listing.product_id == product_id, Listing.url.like("https://example.com/%"))
        ).first()
        is not None
    )


def _marketplace_slugs(db: Session, product_id: int) -> set[str]:
    rows = db.execute(
        select(Marketplace.slug)
        .join(Listing, Listing.marketplace_id == Marketplace.id)
        .where(Listing.product_id == product_id)
    ).all()
    return {slug for (slug,) in rows}


def _score(a: str, b: str) -> tuple[float, float]:
    """Return (similarity, token_coverage)."""
    core_a, full_a = _token_sets(a)
    core_b, full_b = _token_sets(b)
    if not core_a or not core_b:
        return 0.0, 0.0
    overlap = core_a & core_b
    if not overlap:
        return 0.0, 0.0
    coverage = min(len(overlap) / len(core_a), len(overlap) / len(core_b))
    similarity = max(
        fuzz.token_set_ratio(" ".join(sorted(core_a)), " ".join(sorted(core_b))),
        fuzz.token_sort_ratio(" ".join(sorted(core_a)), " ".join(sorted(core_b))),
    )
    return float(similarity), float(coverage)


def _log_low_confidence(matches: list[dict], run_stamp: str) -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    path = LOG_DIR / "low_confidence_matches.csv"
    fresh = not path.exists()
    with path.open("a", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=["run", "product_a_id", "product_a_name", "product_b_id", "product_b_name", "confidence"],
        )
        if fresh:
            writer.writeheader()
        for m in matches:
            writer.writerow(
                {
                    "run": run_stamp,
                    "product_a_id": m["a_id"],
                    "product_a_name": m["a_name"],
                    "product_b_id": m["b_id"],
                    "product_b_name": m["b_name"],
                    "confidence": round(m["confidence"], 2),
                }
            )


def build_matches(
    db_session: Session | None = None,
    log_low_confidence: bool = True,
) -> tuple[int, int]:
    """Match equivalent products across marketplaces (RapidFuzz).

    Returns (created, low_confidence_logged). Only real (non-seed) products
    participate, and only pairs that share no marketplace.
    """
    close = db_session if db_session is not None else SessionLocal()
    try:
        with close as db:
            products = db.execute(select(Product)).scalars().all()
            if not products:
                return 0, 0

            slugs_by_product = {
                p.id: _marketplace_slugs(db, p.id) for p in products
            }
            by_category: dict[str, list[Product]] = {}
            for p in products:
                if not slugs_by_product[p.id]:
                    continue
                by_category.setdefault(p.category, []).append(p)

            run_stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            created = 0
            low_conf: list[dict] = []

            for category, group in by_category.items():
                for i in range(len(group)):
                    for j in range(i + 1, len(group)):
                        a, b = group[i], group[j]
                        if slugs_by_product[a.id] & slugs_by_product[b.id]:
                            continue
                        if _is_seed_product(db, a.id) or _is_seed_product(db, b.id):
                            continue

                        sim, coverage = _score(normalize_name(a.name), normalize_name(b.name))
                        if sim >= HIGH_THRESHOLD and coverage >= MIN_COVERAGE:
                            existing = db.scalar(
                                select(ProductMatch).where(
                                    ProductMatch.product_a_id == a.id,
                                    ProductMatch.product_b_id == b.id,
                                )
                            )
                            if existing is None:
                                db.add(
                                    ProductMatch(
                                        product_a_id=a.id,
                                        product_b_id=b.id,
                                        confidence=round(sim * coverage, 2),
                                        method="rapidfuzz",
                                    )
                                )
                                created += 1
                        elif sim >= LOW_THRESHOLD and coverage >= LOW_COVERAGE:
                            low_conf.append(
                                {
                                    "a_id": a.id,
                                    "a_name": a.name,
                                    "b_id": b.id,
                                    "b_name": b.name,
                                    "confidence": round(sim * coverage, 2),
                                }
                            )

            db.commit()
            if log_low_confidence and low_conf:
                _log_low_confidence(low_conf, run_stamp)
            return created, len(low_conf)
    finally:
        if db_session is None:
            close.close()


if __name__ == "__main__":
    created, logged = build_matches()
    print(f"matches created: {created}")
    print(f"low-confidence pairs logged: {logged}")