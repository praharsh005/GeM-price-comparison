from fastapi.testclient import TestClient
from sqlalchemy import select

from app.database import SessionLocal
from app.main import app
from app.models import Product, ProductMatch

client = TestClient(app)


def _product_id(name_fragment: str) -> int:
    with SessionLocal() as db:
        return db.scalar(
            select(Product.id).where(Product.name.ilike(f"%{name_fragment}%"))
        )


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_categories():
    r = client.get("/categories")
    assert r.status_code == 200
    cats = r.json()
    assert len(cats) == 19
    assert {c["category"] for c in cats} == {
        "Appliances",
        "Audio",
        "Cameras",
        "Computers",
        "Furniture",
        "Grooming",
        "Home",
        "Laptops",
        "Lighting",
        "Medical",
        "Mobile Phones",
        "Monitors",
        "Office",
        "Oxygen Concentrators",
        "Peripherals",
        "Printers",
        "Storage",
        "Televisions",
        "Wearables",
    }
    assert all(c["product_count"] > 0 for c in cats)


def test_search_no_query_returns_all():
    r = client.get("/search")
    assert r.status_code == 200
    results = r.json()
    assert len(results) >= 20
    for item in results:
        assert item["marketplace_count"] >= 1
        assert item["lowest_price"] is not None


def test_search_by_query():
    r = client.get("/search", params={"q": "laptop"})
    assert r.status_code == 200
    results = r.json()
    assert len(results) >= 1
    laptop = [i for i in results if "laptop" in i["name"].lower()]
    assert laptop
    assert laptop[0]["category"] == "Laptops"


def test_search_by_category():
    r = client.get("/search", params={"category": "Audio"})
    assert r.status_code == 200
    results = r.json()
    assert len(results) >= 2
    assert all(item["category"] == "Audio" for item in results)


def test_compare_product():
    pid = _product_id("HP 15s")
    r = client.get(f"/products/{pid}/compare")
    assert r.status_code == 200
    body = r.json()
    assert body["name"] == "HP 15s Laptop"
    assert len(body["listings"]) == 5
    assert body["best_price"] == min(l["price"] for l in body["listings"])
    cheapest = [l for l in body["listings"] if l["is_cheapest"]]
    assert len(cheapest) == 1
    assert cheapest[0]["price"] == body["best_price"]


def test_compare_missing_product_404():
    r = client.get("/products/9999/compare")
    assert r.status_code == 404
    assert r.json()["detail"] == "Product not found"


def test_price_history_shape():
    pid = _product_id("HP 15s")
    r = client.get(f"/products/{pid}/price-history")
    assert r.status_code == 200
    body = r.json()
    assert body["name"] == "HP 15s Laptop"
    assert len(body["series"]) == 5
    for series in body["series"]:
        assert len(series["points"]) >= 2
        for point in series["points"]:
            assert point["price"] > 0
            assert point["recorded_at"]


def test_price_history_missing_product_404():
    r = client.get("/products/9999/price-history")
    assert r.status_code == 404


def test_insights_shape():
    r = client.get("/insights")
    assert r.status_code == 200
    body = r.json()
    assert len(body["categories"]) >= 5
    assert body["overall"]["products_with_gem"] > 0
    assert all(c["avg_savings"] >= 0 for c in body["categories"])
    assert all(c["products_with_gem"] > 0 for c in body["categories"])


def test_alerts_shape():
    r = client.get("/alerts")
    assert r.status_code == 200
    alerts = r.json()
    assert len(alerts) >= 1
    for alert in alerts:
        assert alert["drop_amount"] > 0
        assert alert["percent_drop"] > 0
        assert alert["new_price"] < alert["old_price"]
        assert alert["marketplace_slug"]
        assert alert["dropped_at"]


def test_trending_shape():
    r = client.get("/trending")
    assert r.status_code == 200
    items = r.json()
    assert len(items) >= 1
    for item in items:
        assert item["savings"] > 0
        assert item["best_price"] is not None
        assert item["second_best_price"] > item["best_price"]
        assert abs(item["savings_pct"] - (item["savings"] / item["best_price"] * 100)) < 0.01


def test_trending_limit():
    r = client.get("/trending", params={"limit": 3})
    assert r.status_code == 200
    assert len(r.json()) == 3


def test_compare_includes_matches_when_present():
    with SessionLocal() as db:
        products = db.execute(select(Product).limit(2)).scalars().all()
        assert len(products) == 2
        a_id, b_id = products[0].id, products[1].id
        match = ProductMatch(
            product_a_id=a_id,
            product_b_id=b_id,
            confidence=90.0,
            method="rapidfuzz",
        )
        db.add(match)
        db.commit()
        match_id = match.id
    try:
        for pid, other_id in ((a_id, b_id), (b_id, a_id)):
            r = client.get(f"/products/{pid}/compare")
            assert r.status_code == 200
            matches = r.json()["matches"]
            assert len(matches) == 1
            assert matches[0]["id"] == other_id
            assert matches[0]["confidence"] == 90.0
            assert matches[0]["method"] == "rapidfuzz"
    finally:
        with SessionLocal() as db:
            db.query(ProductMatch).filter(ProductMatch.id == match_id).delete()
            db.commit()
