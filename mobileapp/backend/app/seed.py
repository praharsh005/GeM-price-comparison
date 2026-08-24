from datetime import timedelta

from sqlalchemy import delete, func, select

from app.database import Base, SessionLocal, engine
from app.models import Listing, Marketplace, PriceHistory, Product, ProductMatch

MARKETPLACES = [
    {"name": "GeM", "slug": "gem", "base_url": "https://gem.gov.in"},
    {"name": "Amazon", "slug": "amazon", "base_url": "https://www.amazon.in"},
    {"name": "Flipkart", "slug": "flipkart", "base_url": "https://www.flipkart.com"},
    {"name": "Vijay Sales", "slug": "vijaysales", "base_url": "https://www.vijaysales.com"},
    {"name": "Snapdeal", "slug": "snapdeal", "base_url": "https://www.snapdeal.com"},
]

PRODUCTS = [
    {
        "name": "Lenovo IdeaPad Slim 3 Intel Core i5 12th Gen",
        "category": "laptops",
        "brand": "Lenovo",
        "description": "15.6 inch FHD laptop, 8GB RAM, 512GB SSD",
        "prices": {"GeM": 42990, "Amazon": 44790, "Flipkart": 43890},
    },
    {
        "name": "HP Pavilion 15 Intel Core i7 12th Gen",
        "category": "laptops",
        "brand": "HP",
        "description": "16GB RAM, 1TB SSD, NVIDIA MX570",
        "prices": {"GeM": 72990, "Amazon": 75990, "Flipkart": 74990},
    },
    {
        "name": "Dell Inspiron 15 Intel Core i3 12th Gen",
        "category": "laptops",
        "brand": "Dell",
        "description": "8GB RAM, 256GB SSD",
        "prices": {"GeM": 35990, "Amazon": 37990, "Flipkart": 36990},
    },
    {
        "name": "Asus Vivobook 15 Intel Core i5 11th Gen",
        "category": "laptops",
        "brand": "Asus",
        "description": "8GB RAM, 512GB SSD",
        "prices": {"GeM": 41490, "Amazon": 42990, "Flipkart": 41990},
    },
    {
        "name": "Acer Aspire 5 Intel Core i5 12th Gen",
        "category": "laptops",
        "brand": "Acer",
        "description": "16GB RAM, 512GB SSD",
        "prices": {"GeM": 49490, "Amazon": 51990, "Flipkart": 50990},
    },
    {
        "name": "Samsung Galaxy M34 5G 128GB",
        "category": "smartphones",
        "brand": "Samsung",
        "description": "6.5 inch AMOLED, 50MP camera, 6000mAh",
        "prices": {"GeM": 16499, "Amazon": 17499, "Flipkart": 16999},
    },
    {
        "name": "Redmi Note 13 Pro 5G 128GB",
        "category": "smartphones",
        "brand": "Redmi",
        "description": "200MP camera, 67W fast charging",
        "prices": {"GeM": 19999, "Amazon": 21999, "Flipkart": 20999},
    },
    {
        "name": "Apple iPhone 13 128GB",
        "category": "smartphones",
        "brand": "Apple",
        "description": "6.1 inch Super Retina XDR, A15 Bionic",
        "prices": {"GeM": 54999, "Amazon": 56999, "Flipkart": 55999},
    },
    {
        "name": "OnePlus Nord CE 3 Lite 5G 128GB",
        "category": "smartphones",
        "brand": "OnePlus",
        "description": "108MP camera, 5000mAh battery",
        "prices": {"GeM": 17999, "Amazon": 18999, "Flipkart": 18499},
    },
    {
        "name": "Google Pixel 7a 128GB",
        "category": "smartphones",
        "brand": "Google",
        "description": "Tensor G2, 64MP camera",
        "prices": {"GeM": 35999, "Amazon": 37999, "Flipkart": 36999},
    },
    {
        "name": "Samsung 55 inch Crystal 4K Smart TV",
        "category": "televisions",
        "brand": "Samsung",
        "description": "4K UHD, Crystal Processor 4K",
        "prices": {"GeM": 38990, "Amazon": 40990, "Flipkart": 39990},
    },
    {
        "name": "LG 43 inch 4K Ultra HD Smart TV",
        "category": "televisions",
        "brand": "LG",
        "description": "4K UHD, AI ThinQ, webOS",
        "prices": {"GeM": 26990, "Amazon": 28990, "Flipkart": 27990},
    },
    {
        "name": "Sony Bravia 43 inch 4K Google TV",
        "category": "televisions",
        "brand": "Sony",
        "description": "4K HDR, Google TV, X1 Processor",
        "prices": {"GeM": 43990, "Amazon": 45990, "Flipkart": 44990},
    },
    {
        "name": "Mi 43 inch X Series 4K Smart TV",
        "category": "televisions",
        "brand": "Mi",
        "description": "4K HDR, PatchWall",
        "prices": {"GeM": 23999, "Amazon": 25999, "Flipkart": 24999},
    },
    {
        "name": "Hisense 50 inch 4K UHD Smart TV",
        "category": "televisions",
        "brand": "Hisense",
        "description": "4K UHD, VIDAA OS",
        "prices": {"GeM": 24990, "Amazon": 26990, "Flipkart": 25990},
    },
    {
        "name": "boAt Rockerz 450 Bluetooth Headphones",
        "category": "audio",
        "brand": "boAt",
        "description": "Over-ear, 40mm drivers, 15 hours battery",
        "prices": {"GeM": 999, "Amazon": 1199, "Flipkart": 1099},
    },
    {
        "name": "Sony WH-CH520 Wireless Headphones",
        "category": "audio",
        "brand": "Sony",
        "description": "On-ear, 35 hours battery, multipoint",
        "prices": {"GeM": 3390, "Amazon": 3990, "Flipkart": 3590},
    },
    {
        "name": "JBL Tune 510BT Wireless Headphones",
        "category": "audio",
        "brand": "JBL",
        "description": "On-ear, Pure Bass, 40 hours battery",
        "prices": {"GeM": 2699, "Amazon": 2999, "Flipkart": 2799},
    },
    {
        "name": "Samsung Galaxy Watch 6 40mm",
        "category": "wearables",
        "brand": "Samsung",
        "description": "AMOLED, GPS, Bluetooth",
        "prices": {"GeM": 19999, "Amazon": 21999, "Flipkart": 20999},
    },
    {
        "name": "Noise ColorFit Pro 5 Smartwatch",
        "category": "wearables",
        "brand": "Noise",
        "description": "1.85 inch display, 7 days battery",
        "prices": {"GeM": 1699, "Amazon": 1899, "Flipkart": 1799},
    },
    {
        "name": "Oxygen Cylinder 10L Medical Grade",
        "category": "medical",
        "brand": "Phillips",
        "description": "Portable oxygen cylinder with regulator and flow meter",
        "prices": {"GeM": 4500, "Amazon": 5200, "Flipkart": 4900},
    },
    {
        "name": "Oxygen Concentrator 5L Portable",
        "category": "medical",
        "brand": "Nidek",
        "description": "5L/min continuous flow, 93% purity, portable design",
        "prices": {"GeM": 42000, "Amazon": 46000, "Flipkart": 44000},
    },
    {
        "name": "Digital BP Monitor Upper Arm",
        "category": "medical",
        "brand": "Omron",
        "description": "Automatic blood pressure monitor with irregular heartbeat detection",
        "prices": {"GeM": 1800, "Amazon": 2100, "Flipkart": 1950},
    },
    {
        "name": "Pulse Oximeter Fingertip",
        "category": "medical",
        "brand": "Dr. Trust",
        "description": "SpO2 and pulse rate monitor, LED display",
        "prices": {"GeM": 450, "Amazon": 550, "Flipkart": 499},
    },
    {
        "name": "Wheelchair Foldable Steel Frame",
        "category": "medical",
        "brand": "Karma",
        "description": "Lightweight foldable wheelchair with detachable footrests",
        "prices": {"GeM": 8500, "Amazon": 9500, "Flipkart": 9000},
    },
    {
        "name": "Ergonomic Office Chair Mesh Back",
        "category": "furniture",
        "brand": "Green Soul",
        "description": "Adjustable lumbar support, 3D armrests, tilt mechanism",
        "prices": {"GeM": 7500, "Amazon": 8500, "Flipkart": 8000},
    },
    {
        "name": "Executive Leather Office Chair",
        "category": "furniture",
        "brand": "Da Urban",
        "description": "High back, genuine leather, pneumatic height adjustment",
        "prices": {"GeM": 12000, "Amazon": 13500, "Flipkart": 12800},
    },
    {
        "name": "Study Chair with Writing Pad",
        "category": "furniture",
        "brand": "Nilkamal",
        "description": "Stackable, foldable writing pad, durable plastic frame",
        "prices": {"GeM": 950, "Amazon": 1150, "Flipkart": 1050},
    },
    {
        "name": "Desktop Computer Intel i5 12th Gen 8GB/512GB",
        "category": "computers",
        "brand": "Dell",
        "description": "OptiPlex SFF, Windows 11 Pro, 3-year warranty",
        "prices": {"GeM": 38000, "Amazon": 41000, "Flipkart": 39500},
    },
    {
        "name": "All-in-One PC Intel i7 12th Gen 16GB/1TB",
        "category": "computers",
        "brand": "HP",
        "description": "23.8 inch FHD display, Windows 11, wireless keyboard/mouse",
        "prices": {"GeM": 68000, "Amazon": 72000, "Flipkart": 70000},
    },
    {
        "name": "Mini PC Intel i5 11th Gen 8GB/256GB",
        "category": "computers",
        "brand": "Intel NUC",
        "description": "Compact form factor, VESA mountable, 4K support",
        "prices": {"GeM": 28000, "Amazon": 30500, "Flipkart": 29000},
    },
    {
        "name": "Workstation Tower Xeon W 32GB/1TB SSD",
        "category": "computers",
        "brand": "Lenovo",
        "description": "ThinkStation P360, NVIDIA T400, Linux ready",
        "prices": {"GeM": 85000, "Amazon": 92000, "Flipkart": 89000},
    },
    {
        "name": "Industrial Air Cooler 50L",
        "category": "appliances",
        "brand": "Symphony",
        "description": "Honeycomb pads, 400 sq ft coverage, auto swing",
        "prices": {"GeM": 8500, "Amazon": 9500, "Flipkart": 9000},
    },
    {
        "name": "Water Purifier RO+UV 8L",
        "category": "appliances",
        "brand": "Kent",
        "description": "RO+UV+UF, TDS controller, 20 LPH purification",
        "prices": {"GeM": 12000, "Amazon": 13500, "Flipkart": 12800},
    },
]


def seed() -> None:
    with SessionLocal() as db:
        db.execute(delete(ProductMatch))
        db.execute(delete(PriceHistory))
        db.execute(delete(Listing))
        db.execute(delete(Product))
        db.execute(delete(Marketplace))

        marketplaces: dict[str, Marketplace] = {}
        for m in MARKETPLACES:
            marketplace = Marketplace(**m)
            db.add(marketplace)
            marketplaces[m["name"]] = marketplace
        db.flush()

        for i, p in enumerate(PRODUCTS):
            product = Product(
                name=p["name"],
                category=p["category"],
                brand=p["brand"],
                description=p["description"],
            )
            db.add(product)
            db.flush()

            for mkt_name, price in p["prices"].items():
                listing = Listing(
                    product_id=product.id,
                    marketplace_id=marketplaces[mkt_name].id,
                    url=f"https://example.com/{marketplaces[mkt_name].slug}/product-{product.id}",
                    price=price,
                )
                db.add(listing)
                db.flush()

                for offset_days in (30, 15, 0):
                    db.add(
                        PriceHistory(
                            listing_id=listing.id,
                            price=round(price * (1 + offset_days * 0.001), 2),
                            recorded_at=listing.last_checked_at - timedelta(days=offset_days),
                        )
                    )

        db.commit()

    with SessionLocal() as db:
        print("marketplaces:", db.scalar(select(func.count()).select_from(Marketplace)))
        print("products:", db.scalar(select(func.count()).select_from(Product)))
        print("listings:", db.scalar(select(func.count()).select_from(Listing)))
        print("price_history:", db.scalar(select(func.count()).select_from(PriceHistory)))


if __name__ == "__main__":
    seed()