"""Tests for the Amazon India scraper (Phase 6)."""

from sqlalchemy import select

from app.database import SessionLocal
from app.models import Listing, Marketplace
from app.scrapers.amazon import AMAZON_NAME, CATEGORIES, parse_products, upsert_item

# A small representative Amazon search-results fragment with two cards.
AMAZON_HTML = """
<div data-asin="B0ABC123" data-component-type="s-search-result" class="s-result-item">
  <h2><span>Acer Aspire 5 Intel Core i5-1245U 12th Gen 15.6 inch Laptop</span></h2>
  <a href="/Acer-Aspire-5-Laptop/dp/B0ABC123"></a>
  <span class="a-price-whole">42,999</span>
  <img class="s-image" src="https://example.com/img1.jpg" />
  <span class="a-icon-alt">4.5 out of 5 stars</span>
</div>
<div data-asin="B0XYZ999" data-component-type="s-search-result" class="s-result-item">
  <h2><span>Samsung 24 inch 75Hz VA Panel Monitor</span></h2>
  <a href="/Samsung-24-inch-VA-Monitor/dp/B0XYZ999"></a>
  <span class="a-price-whole">9,499</span>
  <img class="s-image" src="https://example.com/img2.jpg" />
  <span class="a-icon-alt">4.2 out of 5 stars</span>
</div>
"""


def test_categories_defined():
    assert set(CATEGORIES) == {"Laptops", "Monitors", "Printers", "Oxygen Concentrators"}
    for kw in CATEGORIES.values():
        assert kw


def test_parse_products_from_html_fragment():
    items = parse_products(AMAZON_HTML, category="Laptops")
    assert len(items) == 2
    first = items[0]
    assert first["title"].startswith("Acer Aspire 5")
    assert first["url"].startswith("https://www.amazon.in/")
    assert first["price"] == 42999.0
    assert first["rating"] == 4.5
    assert first["category"] == "Laptops"
    assert first["asin"] == "B0ABC123"


def test_upsert_is_idempotent():
    """Inserting the same item twice does not create duplicate listings."""
    db = SessionLocal()
    try:
        amazon = db.scalar(select(Marketplace).where(Marketplace.name == AMAZON_NAME))
        if amazon is None:
            amazon = Marketplace(name=AMAZON_NAME, base_url="https://www.amazon.in")
            db.add(amazon)
            db.flush()

        item = {
            "title": "Acer Aspire 5 Intel Core i5-1245U 12th Gen 15.6 inch Laptop",
            "url": "https://www.amazon.in/dp/B0ABC123",
            "category": "Laptops",
            "price": 42999.0,
            "image_url": "https://example.com/img1.jpg",
            "rating": 4.5,
            "asin": "B0ABC123",
        }
        l1 = upsert_item(db, item, amazon)
        l2 = upsert_item(db, item, amazon)

        assert l1.id == l2.id
        count = db.query(Listing).filter(
            Listing.marketplace_id == amazon.id, Listing.url == item["url"]
        ).count()
        assert count == 1
        assert l1.match_confidence is None or 0 <= l1.match_confidence <= 100
    finally:
        db.rollback()
        db.close()
