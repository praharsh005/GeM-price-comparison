from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_search_empty_result_is_200():
    r = client.get("/search", params={"q": "zzzznothing"})
    assert r.status_code == 200
    assert r.json() == []


def test_search_nonexistent_category_is_200():
    r = client.get("/search", params={"category": "xyz"})
    assert r.status_code == 200
    assert r.json() == []


def test_search_like_wildcard_percent_is_escaped():
    r = client.get("/search", params={"q": "%"})
    assert r.status_code == 200
    assert all("%" in item["name"] for item in r.json())


def test_search_like_wildcard_underscore_is_escaped():
    r = client.get("/search", params={"q": "_"})
    assert r.status_code == 200
    assert all("_" in item["name"] for item in r.json())


def test_search_empty_q_returns_all_without_500():
    r = client.get("/search", params={"q": ""})
    assert r.status_code == 200
    assert len(r.json()) >= 20


def test_search_special_chars_no_500():
    for q in ["%", "_", "\\", "'", '"', "100%", "A_B", "₹", "é"]:
        r = client.get("/search", params={"q": q})
        assert r.status_code == 200, f"q={q!r} failed"


def test_compare_non_int_422():
    r = client.get("/products/abc/compare")
    assert r.status_code == 422


def test_compare_missing_product_404():
    r = client.get("/products/99999/compare")
    assert r.status_code == 404


def test_compare_scraped_product_with_null_fields():
    r = client.get("/search", params={"q": "oxygen"})
    results = r.json()
    assert len(results) >= 1
    pid = results[0]["id"]
    r = client.get(f"/products/{pid}/compare")
    assert r.status_code == 200
    body = r.json()
    assert body["listings"]
    assert body["best_price"] is not None
    assert body["best_marketplace"] == "GeM"


def test_categories_include_scraped_category():
    r = client.get("/categories")
    assert r.status_code == 200
    cats = {c["category"] for c in r.json()}
    assert "Laptops" in cats
