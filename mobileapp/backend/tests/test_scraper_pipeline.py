from sqlalchemy import func, select

from app.database import SessionLocal
from app.models import Listing, Marketplace, Product
from scrapers.pipelines import GemPipeline

ITEM = {
    "name": "Test Laptop X1 2026",
    "brand": "TestBrand",
    "category": "laptops",
    "url": "https://mkp.gem.gov.in/test-laptop-x1/p-9999-test-cat.html",
    "price": 25000.0,
    "mrp": 30000.0,
    "availability": True,
    "image_url": None,
}


def test_pipeline_creates_and_is_idempotent():
    pipeline = GemPipeline()
    with SessionLocal() as db:
        before = db.scalar(
            select(func.count(Listing.id)).where(Listing.url == ITEM["url"])
        )
        assert before == 0

    pipeline.process_item(dict(ITEM), None)
    pipeline.process_item(dict(ITEM), None)
    pipeline.process_item(dict(ITEM), None)

    with SessionLocal() as db:
        listing = db.scalar(select(Listing).where(Listing.url == ITEM["url"]))
        assert listing is not None
        assert listing.price == 25000.0

        product = db.get(Product, listing.product_id)
        assert product.name == ITEM["name"]
        assert product.category == "laptops"
        assert product.brand == "TestBrand"

        marketplace = db.get(Marketplace, listing.marketplace_id)
        assert marketplace.slug == "gem"

        count = db.scalar(select(func.count(Listing.id)).where(Listing.url == ITEM["url"]))
        assert count == 1

    with SessionLocal() as db:
        db.execute(
            Listing.__table__.delete().where(Listing.url == ITEM["url"])
        )
        db.execute(Product.__table__.delete().where(Product.name == ITEM["name"]))
        db.commit()