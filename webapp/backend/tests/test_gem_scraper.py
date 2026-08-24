"""Tests for the GeM category scraper.

These hit the live GeM category pages, so they are integration tests.
They intentionally limit scraping to a single page to keep them quick.
"""

import logging

from sqlalchemy import select

from app.database import SessionLocal
from app.models import Listing, Marketplace, Product
from app.scrapers.gem import CATEGORIES, GEM_NAME, HEADERS, parse_products, run


def _gem_listing_count(db):
    gem = db.scalar(select(Marketplace).where(Marketplace.name == GEM_NAME))
    if gem is None:
        return 0
    return db.query(Listing).filter(Listing.marketplace_id == gem.id).count()


def test_parse_products_from_live_page():
    """Parsing a live category page yields product cards with required fields."""
    import requests

    from app.scrapers.gem import BASE_URL

    category, path = list(CATEGORIES.items())[0]
    url = BASE_URL + path
    resp = requests.get(url, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    products = parse_products(resp.text, category)
    assert len(products) > 0
    for p in products:
        assert p["title"]
        assert p["url"].startswith("https://mkp.gem.gov.in/")
        assert p["price"] and p["price"] > 0
        assert p["category"] == category


def test_scrape_produces_rows():
    db = SessionLocal()
    try:
        before = _gem_listing_count(db)
        run(max_pages=1)
        after = _gem_listing_count(db)
        assert after >= before
        assert after > 0
        assert db.query(Product).count() > 0
    finally:
        db.close()


def test_scrape_is_idempotent():
    db = SessionLocal()
    try:
        run(max_pages=1)
        products_1 = db.query(Product).count()
        listings_1 = db.query(Listing).count()
        run(max_pages=1)
        products_2 = db.query(Product).count()
        listings_2 = db.query(Listing).count()
        assert products_2 == products_1
        assert listings_2 == listings_1
    finally:
        db.close()


def test_rate_limit_applied(caplog):
    with caplog.at_level(logging.INFO, logger="app.scrapers.gem"):
        run(max_pages=1)
    rate_msgs = [r for r in caplog.records if "Rate-limited" in r.getMessage()]
    assert len(rate_msgs) >= 1
