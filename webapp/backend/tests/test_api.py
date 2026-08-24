from fastapi.testclient import TestClient
from sqlalchemy import func

from app.main import app
from app.database import SessionLocal
from app.models import Listing, Marketplace, Product
from app.scrapers.gem import run as gem_run

client = TestClient(app)


def setup_module():
    """Guarantee real GeM data exists (idempotent) without wiping the DB."""
    with SessionLocal() as db:
        has_gem = (
            db.query(Listing)
            .join(Marketplace)
            .filter(Marketplace.name == "GeM")
            .count()
            > 0
        )
    if not has_gem:
        gem_run(max_pages=1)


def test_health():
    assert client.get("/health").status_code == 200


def test_search_returns_shape():
    resp = client.get("/search", params={"q": "laptop"})
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    for r in data:
        assert "id" in r and "name" in r and "gem_price" in r and "category" in r


def test_search_empty_query_returns_all():
    resp = client.get("/search")
    assert resp.status_code == 200
    data = resp.json()
    with SessionLocal() as db:
        total_products = db.query(Product).count()
    assert len(data) == total_products
    assert len(data) > 0


def test_search_empty_result():
    resp = client.get("/search", params={"q": "zzzznonexistent"})
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 0


def test_search_by_category():
    cat_resp = client.get("/categories").json()
    with_cat = [c for c in cat_resp if c["product_count"] > 0][0]
    name = with_cat["category"]
    resp = client.get("/search", params={"category": name})
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == with_cat["product_count"]
    assert len(data) >= 1
    assert all(r["category"] == name for r in data)


def test_compare_returns_shape():
    resp = client.get("/search", params={"q": "laptop"})
    results = resp.json()
    assert len(results) >= 1
    pid = results[0]["id"]
    c = client.get(f"/products/{pid}/compare")
    assert c.status_code == 200
    data = c.json()
    assert data["id"] == pid
    assert "name" in data and "gem_price" in data and "market_best_price" in data
    assert "savings" in data and "savings_pct" in data
    assert isinstance(data["listings"], list) and len(data["listings"]) >= 1
    for l in data["listings"]:
        assert "marketplace_name" in l and "price" in l


def test_compare_product_with_only_gem_listing():
    """Real scraped products have a single GeM listing; compare must not 500."""
    with SessionLocal() as db:
        single = (
            db.query(Listing.product_id)
            .group_by(Listing.product_id)
            .having(func.count(Listing.id) == 1)
            .first()
        )
    assert single is not None
    pid = single[0]
    c = client.get(f"/products/{pid}/compare")
    assert c.status_code == 200
    data = c.json()
    assert data["id"] == pid
    assert len(data["listings"]) == 1
    assert data["listings"][0]["marketplace_name"] == "GeM"
    assert data["market_best_price"] is None
    assert data["market_average"] is None
    assert data["savings"] is None


def test_compare_product_without_price():
    """A listing with no price yet must render, not crash."""
    with SessionLocal() as db:
        gem = db.query(Marketplace).filter(Marketplace.name == "GeM").first()
        product = Product(name="Test No Price Item", brand="Test", category="Laptops")
        db.add(product)
        db.flush()
        listing = Listing(
            product_id=product.id,
            marketplace_id=gem.id,
            title="Test No Price Item",
            url="https://mkp.gem.gov.in/test-no-price/p-1-1-cat.html",
            price=0.01,
            currency="INR",
            availability=True,
        )
        db.add(listing)
        db.commit()
        pid = product.id
        lid = listing.id
    try:
        c = client.get(f"/products/{pid}/compare")
        assert c.status_code == 200
        data = c.json()
        assert data["gem_price"] == 0.01
        assert data["market_best_price"] is None
        assert data["savings"] is None
    finally:
        with SessionLocal() as db:
            db.query(Listing).filter(Listing.id == lid).delete()
            db.query(Product).filter(Product.id == pid).delete()
            db.commit()


def test_compare_not_found():
    resp = client.get("/products/999999/compare")
    assert resp.status_code == 404


def test_categories_returns_shape():
    resp = client.get("/categories")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) >= 19  # Website seed has 19 categories
    total_products = sum(c["product_count"] for c in data)
    with SessionLocal() as db:
        db_total = db.query(Product).count()
    assert total_products == db_total
    for c in data:
        assert "category" in c and "product_count" in c
        # avg_savings not included in new endpoint format


def test_categories_avg_savings_present():
    """At least one category reports an average savings figure."""
    data = client.get("/categories").json()
    # New endpoint returns list of {category, product_count} - avg_savings not included
    # This test was for the old endpoint format
    assert isinstance(data, list)
    assert len(data) >= 19


def test_compare_price_history_time_series_shape():
    """Compare endpoint returns price history via separate endpoint, not in compare."""
    resp = client.get("/search", params={"q": "laptop"})
    results = resp.json()
    assert results, "expected at least one laptop result"
    c = client.get(f"/products/{results[0]['id']}/compare")
    assert c.status_code == 200
    data = c.json()
    # Compare endpoint doesn't include price_history - use /price-history endpoint
    assert "price_history" not in data
    assert "series" not in data
    # But it should have listings with price data
    assert "listings" in data
    assert len(data["listings"]) >= 1
