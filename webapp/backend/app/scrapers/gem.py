"""GeM marketplace category scraper (server-rendered search pages).

Fetches public GeM marketplace category search pages, which are
server-rendered (no JS/XHR required), parses the product cards with
lxml, and writes them into the Phase 1 schema (products / marketplaces
/ listings / price_history).

Rate-limited and idempotent:
- a configurable delay is applied between HTTP requests,
- re-running the scraper updates existing listings instead of creating
  duplicate rows (keyed on the listing URL).

Run directly: `python -m app.scrapers.gem [--pages N] [--fresh]`
"""

import argparse
import logging
import re
import time
from datetime import datetime, timezone
from urllib.parse import urljoin

import requests
from lxml import html
from sqlalchemy import select

from app.config import settings
from app.database import SessionLocal
from app.models import Listing, Marketplace, PriceHistory, Product

logger = logging.getLogger(__name__)

BASE_URL = "https://mkp.gem.gov.in"
GEM_NAME = "GeM"

CATEGORIES = {
    "Laptops": "/computers-entry-and-mid-level-laptop-notebook/search",
    "Monitors": "/computer-displays-computer-monitor-v2-/search",
    "Printers": "/information-technology-broadcasting-and-telecommunications-computer-equipment-and-accessoriesold-computer-printers-computer-printer-v2-/search",
    "Oxygen Concentrators": "/oxygen-therapy-delivery-systems-and-devices-oxygen-concentrator-v2-/search",
}

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/125.0 Safari/537.36"
    ),
    "Accept-Language": "en-IN,en;q=0.9",
}

_PRICE_RE = re.compile(r"[\d,]+\.?\d*")


def _parse_price(text):
    """Extract a float from a localized price string like 'Rs. 1,16,571.50'."""
    match = _PRICE_RE.search(text.replace(",", "").replace("\u20b9", "").strip())
    return float(match.group(0)) if match else None


def _clean(text):
    return re.sub(r"\s+", " ", text).strip()


def fetch_page(session, category_path, page, rate_limit):
    """Fetch one search-results page, applying the configured rate limit."""
    params = {"bis": "true", "don_load_facets": "true", "home": "false", "page": str(page)}
    url = urljoin(BASE_URL, category_path)
    logger.info("Fetching GeM category page %s (page %s)", category_path, page)
    resp = session.get(url, params=params, timeout=30)
    resp.raise_for_status()
    logger.info("GeM page %s: HTTP %s, %s bytes", page, resp.status_code, len(resp.content))
    logger.info("Rate-limited: sleeping %.1fs", rate_limit)
    time.sleep(rate_limit)
    return resp.text


def parse_products(html_text, category="Laptops"):
    """Parse product cards from a category search page into dicts."""
    doc = html.fromstring(html_text)
    cards = doc.xpath("//li[contains(@class,'clearfix') and .//div[contains(@class,'variant-wrapper')]]")
    products = []
    for card in cards:
        title = _clean(card.xpath("string(.//span[contains(@class,'variant-title')]/a/@title)"))
        href = card.xpath("string(.//div[contains(@class,'variant-image')]/a/@href)").strip()
        if not title or not href:
            continue
        brand = _clean(card.xpath("string(.//div[contains(@class,'variant-brand')])")).replace("Brand:", "").strip()
        list_price = _parse_price(card.xpath("string(.//span[contains(@class,'variant-list-price')]/span[contains(@class,'m-w')])"))
        final_price = _parse_price(card.xpath("string(.//span[contains(@class,'variant-final-price')]/span[contains(@class,'m-w')])"))
        image_url = card.xpath("string(.//div[contains(@class,'variant-image')]//span[@data-src]/@data-src)").strip()
        products.append({
            "title": title,
            "url": urljoin(BASE_URL, href),
            "brand": brand,
            "category": category,
            "list_price": list_price,
            "price": final_price or list_price,
            "image_url": image_url,
        })
    return products


def upsert_product(db, item, gem_marketplace):
    """Insert a scraped item or update the existing listing (idempotent)."""
    existing = db.scalar(
        select(Listing).where(
            Listing.marketplace_id == gem_marketplace.id,
            Listing.url == item["url"],
        )
    )
    if existing:
        changed = existing.price != item["price"]
        existing.title = item["title"]
        existing.price = item["price"]
        existing.image_url = item["image_url"] or existing.image_url
        existing.scraped_at = datetime.now(timezone.utc)
        if changed:
            db.add(PriceHistory(listing_id=existing.id, price=item["price"]))
        return existing

    product = Product(
        name=item["title"],
        brand=item["brand"] or None,
        category=item["category"],
    )
    db.add(product)
    db.flush()
    listing = Listing(
        product_id=product.id,
        marketplace_id=gem_marketplace.id,
        title=item["title"],
        url=item["url"],
        image_url=item["image_url"] or None,
        price=item["price"],
        currency="INR",
        availability=True,
    )
    db.add(listing)
    db.flush()
    db.add(PriceHistory(listing_id=listing.id, price=item["price"]))
    return listing


def run(max_pages=None, fresh=False, categories=None):
    """Scrape GeM categories into the database. Returns row counts."""
    pages = max_pages or settings.scraper_max_pages
    cats = categories or CATEGORIES
    db = SessionLocal()
    try:
        gem = db.scalar(select(Marketplace).where(Marketplace.name == GEM_NAME))
        if gem is None:
            gem = Marketplace(name=GEM_NAME, base_url=BASE_URL)
            db.add(gem)
            db.flush()

        if fresh:
            gem_listing_ids = [
                lid for (lid,) in db.query(Listing.id).filter(Listing.marketplace_id == gem.id).all()
            ]
            db.query(PriceHistory).filter(PriceHistory.listing_id.in_(gem_listing_ids)).delete(
                synchronize_session=False
            )
            db.query(Listing).filter(Listing.marketplace_id == gem.id).delete(
                synchronize_session=False
            )
            orphan_ids = [
                pid
                for (pid,) in db.query(Product.id).all()
                if db.query(Listing).filter(Listing.product_id == pid).count() == 0
            ]
            if orphan_ids:
                db.query(Product).filter(Product.id.in_(orphan_ids)).delete(
                    synchronize_session=False
                )
            db.commit()

        session = requests.Session()
        session.headers.update(HEADERS)
        for category, path in cats.items():
            for page in range(1, pages + 1):
                html_text = fetch_page(session, path, page, settings.scraper_rate_limit)
                items = parse_products(html_text, category)
                if not items:
                    logger.info("No products on %s page %s; stopping", category, page)
                    break
                for item in items:
                    upsert_product(db, item, gem)
                db.commit()
            logger.info("Category %s done", category)

        counts = {
            "products": db.query(Product).count(),
            "listings": db.query(Listing).count(),
            "price_history": db.query(PriceHistory).count(),
        }
        logger.info("GeM scrape done: %s", counts)
        return counts
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scrape GeM categories")
    parser.add_argument("--pages", type=int, default=None, help="Max pages to scrape")
    parser.add_argument("--fresh", action="store_true", help="Delete existing GeM listings first")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO)
    print(run(max_pages=args.pages, fresh=args.fresh))
