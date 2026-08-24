from datetime import datetime, timezone

from sqlalchemy import select

from app.database import SessionLocal
from app.models import Listing, Marketplace, PriceHistory, Product

SOURCE_MARKETPLACE_SLUG = "gem"


class MarketplacePipeline:
    def __init__(self, marketplace_slug: str = SOURCE_MARKETPLACE_SLUG):
        self.marketplace_slug = marketplace_slug

    def process_item(self, item, spider=None):
        with SessionLocal() as db:
            marketplace = db.scalar(
                select(Marketplace).where(Marketplace.slug == self.marketplace_slug)
            )
            if marketplace is None:
                raise RuntimeError(
                    f"Marketplace slug '{self.marketplace_slug}' not found — run the seed first"
                )

            listing = db.scalar(select(Listing).where(Listing.url == item["url"]))
            if listing is None:
                product = db.scalar(
                    select(Product).where(
                        Product.name == item["name"], Product.category == item["category"]
                    )
                )
                if product is None:
                    product = Product(
                        name=item["name"],
                        category=item["category"],
                        brand=item["brand"],
                        image_url=item.get("image_url"),
                    )
                    db.add(product)
                    db.flush()
                else:
                    existing = db.scalar(
                        select(Listing).where(
                            Listing.product_id == product.id,
                            Listing.marketplace_id == marketplace.id,
                        )
                    )
                    if existing is not None:
                        existing.url = item["url"]
                        existing.price = item["price"]
                        existing.availability = item["availability"]
                        existing.last_checked_at = datetime.now(timezone.utc)
                        db.add(existing)
                        db.add(PriceHistory(listing_id=existing.id, price=item["price"]))
                        db.commit()
                        return item

                listing = Listing(
                    product_id=product.id,
                    marketplace_id=marketplace.id,
                    url=item["url"],
                    price=item["price"],
                    availability=item["availability"],
                )
                db.add(listing)
                db.flush()
            else:
                listing.price = item["price"]
                listing.availability = item["availability"]
                listing.last_checked_at = datetime.now(timezone.utc)
                db.add(listing)

            db.add(PriceHistory(listing_id=listing.id, price=item["price"]))
            db.commit()

        return item


class GemPipeline(MarketplacePipeline):
    def __init__(self):
        super().__init__(SOURCE_MARKETPLACE_SLUG)
