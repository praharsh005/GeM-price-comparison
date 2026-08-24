from sqlalchemy import func, select

from app.database import SessionLocal
from app.models import Listing, Marketplace, PriceHistory, Product


def _count(model):
    with SessionLocal() as db:
        return db.scalar(select(func.count()).select_from(model))


def test_seed_counts():
    # Website seed: 5 marketplaces, 37+ products, 173+ listings, 346+ price history
    assert _count(Marketplace) == 5
    assert _count(Product) >= 37
    assert _count(Listing) >= 173
    assert _count(PriceHistory) >= 346


def test_seed_products_have_marketplace_listings():
    with SessionLocal() as db:
        rows = db.execute(
            select(Product.id, func.count(Listing.id))
            .join(Listing, Listing.product_id == Product.id)
            .group_by(Product.id)
            .having(func.count(Listing.id) >= 3)
        ).all()

    assert len(rows) >= 20


def test_product_shape():
    with SessionLocal() as db:
        product = db.scalar(select(Product).where(Product.name.ilike("%laptop%")))

    assert product is not None
    assert product.category in ("Laptops", "laptops")
    assert product.brand
    assert product.created_at is not None


def test_every_product_has_marketplace_listings():
    with SessionLocal() as db:
        rows = db.execute(
            select(Product.id, func.count(Listing.id))
            .join(Listing, Listing.product_id == Product.id)
            .group_by(Product.id)
        ).all()

    assert len(rows) >= 20
    assert all(count >= 1 for _, count in rows)


def test_each_listing_has_price_history():
    with SessionLocal() as db:
        rows = db.execute(
            select(Listing.id, func.count(PriceHistory.id))
            .join(PriceHistory, PriceHistory.listing_id == Listing.id)
            .group_by(Listing.id)
        ).all()

    assert len(rows) >= 173
    assert all(count >= 1 for _, count in rows)


def test_compare_query_shape():
    with SessionLocal() as db:
        rows = db.execute(
            select(
                Product.name.label("product_name"),
                Marketplace.name.label("marketplace_name"),
                Listing.price.label("price"),
            )
            .join(Listing, Listing.product_id == Product.id)
            .join(Marketplace, Marketplace.id == Listing.marketplace_id)
            .where(Product.name.ilike("%laptop%"))
            .order_by(Listing.price)
        ).all()

    # Website seed has 5 marketplaces, so up to 5 listings per laptop
    assert len(rows) >= 3
    names = [row.marketplace_name for row in rows]
    assert set(names) >= {"GeM", "Amazon", "Flipkart"}
    assert all(row.price > 0 for row in rows)
    assert rows[0].price == min(row.price for row in rows)


def test_no_duplicate_listing_per_product_marketplace():
    with SessionLocal() as db:
        dupes = db.execute(
            select(Listing.product_id, Listing.marketplace_id, func.count())
            .group_by(Listing.product_id, Listing.marketplace_id)
            .having(func.count() > 1)
        ).all()

    assert len(dupes) == 0