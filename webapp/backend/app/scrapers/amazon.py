"""Amazon India search scraper.

Fetches public Amazon.in search result pages (`/s?k=...`), which are
allowed by Amazon's robots.txt for a generic user agent, parses the
product cards with lxml, and writes them into the Phase 1 schema.

Each parsed item is matched against existing GeM products with the
RapidFuzz matching layer (`app.matching`). When a confident match is
found the Amazon listing is attached to the *same* `products` row as the
GeM listing; otherwise a new product row is created and the outcome is
logged for manual review.

Rate-limited and idempotent, keyed on the listing URL (mirrors the GeM
scraper). Run directly: `python -m app.scrapers.amazon [--pages N]`
"""

import argparse
import logging
import time
from datetime import datetime, timezone
from urllib.parse import urljoin

import requests
from lxml import html
from sqlalchemy import select

from app.config import settings
from app.database import SessionLocal
from app.matching import MATCH_THRESHOLD, decide, find_best_gem_product, log_review
from app.models import Listing, Marketplace, PriceHistory, Product

logger = logging.getLogger(__name__)

BASE_URL = "https://www.amazon.in"
AMAZON_NAME = "Amazon"

# Category name -> Amazon search keyword.
CATEGORIES = {
    "Laptops": "laptop",
    "Monitors": "computer monitor",
    "Printers": "printer",
    "Oxygen Concentrators": "oxygen concentrator",
}

HEADERS = {
    "User-Agent": (
        "GeMPriceIntelligenceResearchBot/0.1 "
        "(educational price comparison project; contact: student@example.com)"
    ),
    "Accept-Language": "en-IN,en;q=0.9",
}

_PRICE_RE = r"[\d,]+\.?\d*"


def fetch_page(session, keyword, page, rate_limit):
    """Fetch one Amazon search-results page, applying the rate limit."""
    params = {"k": keyword, "page": str(page), "ref": "nb_sb_noss"}
    url = urljoin(BASE_URL, "/s")
    logger.info("Fetching Amazon search %r (page %s)", keyword, page)
    resp = session.get(url, params=params, timeout=30)
    resp.raise_for_status()
    logger.info("Amazon page %s: HTTP %s, %s bytes", page, resp.status_code, len(resp.content))
    logger.info("Rate-limited: sleeping %.1fs", rate_limit)
    time.sleep(rate_limit)
    return resp.text


def _parse_price(text):
    if not text:
        return None
    import re

    m = re.search(_PRICE_RE, text.replace(",", "").strip())
    return float(m.group(0)) if m else None


def _clean(text, max_len=255):
    import re

    text = re.sub(r"\s+", " ", text).strip()
    return text[:max_len] if max_len else text


def parse_products(html_text, category="Laptops"):
    """Parse product cards from an Amazon search page into dicts."""
    doc = html.fromstring(html_text)
    cards = doc.xpath(
        "//div[contains(@class,'s-result-item') and @data-asin "
        "and @data-component-type='s-search-result']"
    )
    products = []
    for card in cards:
        title = _clean(card.xpath("string(.//h2/span)"))
        if not title:
            continue
        href = card.xpath("string(.//h2/a/@href)").strip()
        if not href:
            links = card.xpath(".//a[contains(@href,'/dp/')]")
            href = links[0].get("href") if links else ""
        if not href:
            continue
        price = _parse_price(card.xpath("string(.//span[contains(@class,'a-price-whole')])"))
        if not price:
            continue
        image_url = card.xpath("string(.//img[contains(@class,'s-image')]/@src)").strip()
        rating_text = card.xpath("string(.//span[contains(@class,'a-icon-alt')])")
        rating = None
        if rating_text:
            import re

            m = re.search(r"([\d.]+)", rating_text)
            rating = float(m.group(1)) if m else None
        asin = (card.get("data-asin") or "").strip()
        products.append({
            "title": title,
            "url": urljoin(BASE_URL, href),
            "category": category,
            "price": price,
            "image_url": image_url,
            "rating": rating,
            "asin": asin,
        })
    return products


def upsert_item(db, item, amazon_marketplace):
    """Insert an Amazon item or update the existing listing (idempotent).

    Attempts to match the item against an existing GeM product. On a
    confident match the Amazon listing is attached to the same product
    row; otherwise a new product row is created.
    """
    existing = db.scalar(
        select(Listing).where(
            Listing.marketplace_id == amazon_marketplace.id,
            Listing.url == item["url"],
        )
    )
    if existing:
        changed = existing.price != item["price"]
        existing.title = item["title"]
        existing.price = item["price"]
        existing.image_url = item["image_url"] or existing.image_url
        existing.rating = item["rating"] or existing.rating
        existing.scraped_at = datetime.now(timezone.utc)
        if changed:
            db.add(PriceHistory(listing_id=existing.id, price=item["price"]))
        return existing

    product, score = find_best_gem_product(db, item["title"], category=item["category"])
    is_match, band = decide(score)

    if is_match and product is not None:
        target = product
        confidence = score
    else:
        target = Product(
            name=item["title"],
            category=item["category"],
        )
        db.add(target)
        db.flush()
        confidence = score if score > 0 else None
        log_review(item["title"], None, score)

    # A product can hold at most one listing per marketplace.
    existing_on_target = db.scalar(
        select(Listing).where(
            Listing.product_id == target.id,
            Listing.marketplace_id == amazon_marketplace.id,
        )
    )
    if existing_on_target is not None:
        changed = existing_on_target.price != item["price"]
        existing_on_target.title = item["title"]
        existing_on_target.url = item["url"]
        existing_on_target.price = item["price"]
        existing_on_target.image_url = item["image_url"] or existing_on_target.image_url
        existing_on_target.rating = item["rating"] or existing_on_target.rating
        existing_on_target.match_confidence = confidence
        existing_on_target.scraped_at = datetime.now(timezone.utc)
        if changed:
            db.add(PriceHistory(listing_id=existing_on_target.id, price=item["price"]))
        return existing_on_target

    listing = Listing(
        product_id=target.id,
        marketplace_id=amazon_marketplace.id,
        title=item["title"],
        url=item["url"],
        image_url=item["image_url"] or None,
        price=item["price"],
        currency="INR",
        availability=True,
        rating=item["rating"],
        match_confidence=confidence,
    )
    db.add(listing)
    db.flush()
    db.add(PriceHistory(listing_id=listing.id, price=item["price"]))
    return listing


def run(max_pages=None, categories=None):
    """Scrape Amazon categories into the database. Returns row counts."""
    pages = max_pages or settings.scraper_max_pages
    cats = categories or CATEGORIES
    db = SessionLocal()
    try:
        amazon = db.scalar(select(Marketplace).where(Marketplace.name == AMAZON_NAME))
        if amazon is None:
            amazon = Marketplace(name=AMAZON_NAME, base_url=BASE_URL)
            db.add(amazon)
            db.flush()

        session = requests.Session()
        session.headers.update(HEADERS)
        matched = unmatched = items = 0
        for category, keyword in cats.items():
            for page in range(1, pages + 1):
                html_text = fetch_page(session, keyword, page, settings.scraper_rate_limit)
                parsed = parse_products(html_text, category)
                if not parsed:
                    logger.info("No products for %s page %s; stopping", category, page)
                    break
                for item in parsed:
                    listing = upsert_item(db, item, amazon)
                    items += 1
                    if listing.match_confidence and listing.match_confidence >= MATCH_THRESHOLD:
                        matched += 1
                    else:
                        unmatched += 1
                db.commit()
            logger.info("Category %s done", category)

        counts = {
            "products": db.query(Product).count(),
            "listings": db.query(Listing).count(),
            "price_history": db.query(PriceHistory).count(),
            "items_seen": items,
            "matched_to_gem": matched,
            "unmatched": unmatched,
        }
        logger.info("Amazon scrape done: %s", counts)
        return counts
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scrape Amazon India categories")
    parser.add_argument("--pages", type=int, default=None, help="Max pages to scrape")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO)
    print(run(max_pages=args.pages))
