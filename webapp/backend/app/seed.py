"""Seed script: ~20 fake products across 3 marketplaces with listings and price history.

Idempotent-safe: run inside a transaction; call via `python -m app.seed`.
"""

from sqlalchemy import text

from app.database import SessionLocal
from app.models import Listing, Marketplace, PriceHistory, Product

MARKETPLACES = [
    {"name": "GeM", "slug": "gem", "base_url": "https://gem.gov.in"},
    {"name": "Amazon", "slug": "amazon", "base_url": "https://www.amazon.in"},
    {"name": "Flipkart", "slug": "flipkart", "base_url": "https://www.flipkart.com"},
    {"name": "Vijay Sales", "slug": "vijaysales", "base_url": "https://www.vijaysales.com"},
    {"name": "Snapdeal", "slug": "snapdeal", "base_url": "https://www.snapdeal.com"},
]

PRODUCTS = [
    {"name": "HP 15s Laptop", "brand": "HP", "model_number": "15s-fq2711TU", "category": "Laptops",
     "description": "Intel Core i3, 8GB RAM, 256GB SSD", "price_range": (28000, 36000)},
    {"name": "Dell Inspiron 3520 Laptop", "brand": "Dell", "model_number": "D560360WIN9", "category": "Laptops",
     "description": "Intel Core i5, 16GB RAM, 512GB SSD", "price_range": (48000, 56000)},
    {"name": "Lenovo IdeaPad Slim 3", "brand": "Lenovo", "model_number": "82XA00BGIN", "category": "Laptops",
     "description": "AMD Ryzen 5, 8GB RAM, 512GB SSD", "price_range": (40000, 47000)},
    {"name": "Logitech MX Master 3S Mouse", "brand": "Logitech", "model_number": "910-006559", "category": "Peripherals",
     "description": "Wireless performance mouse", "price_range": (4200, 6000)},
    {"name": "Samsung 24 inch Monitor", "brand": "Samsung", "model_number": "LS24C310EAWXXL", "category": "Monitors",
     "description": "Full HD IPS display", "price_range": (6500, 8500)},
    {"name": "Canon EOS R50 Camera", "brand": "Canon", "model_number": "EOS R50", "category": "Cameras",
     "description": "Mirrorless camera with 24.2MP", "price_range": (62000, 72000)},
    {"name": "Bosch Dishwasher 14 Place", "brand": "Bosch", "model_number": "SMS46NI02I", "category": "Appliances",
     "description": "Freestanding dishwasher", "price_range": (40000, 49000)},
    {"name": "JBL Flip 6 Speaker", "brand": "JBL", "model_number": "JBLFLIP6BLK", "category": "Audio",
     "description": "Portable Bluetooth speaker", "price_range": (7200, 9500)},
    {"name": "Xiaomi Smart TV 43 inch", "brand": "Xiaomi", "model_number": "X43F", "category": "Televisions",
     "description": "4K UHD smart TV", "price_range": (25000, 31000)},
    {"name": "ASUS ROG Strix G16", "brand": "ASUS", "model_number": "G614JV-AS73", "category": "Laptops",
     "description": "RTX 4060 gaming laptop", "price_range": (115000, 130000)},
    {"name": "Philips Trimmer 7000", "brand": "Philips", "model_number": "MG7715/15", "category": "Grooming",
     "description": "Multigroom series 7000", "price_range": (2400, 3400)},
    {"name": "OnePlus Nord CE 4", "brand": "OnePlus", "model_number": "Nord CE 4", "category": "Mobile Phones",
     "description": "5G smartphone 8GB/128GB", "price_range": (22000, 25000)},
    {"name": "Sony WH-1000XM5 Headphones", "brand": "Sony", "model_number": "WH1000XM5", "category": "Audio",
     "description": "Wireless noise cancelling headphones", "price_range": (26000, 30000)},
    {"name": "IFB Washing Machine 7kg", "brand": "IFB", "model_number": "WFOOT7S", "category": "Appliances",
     "description": "Front load 7kg", "price_range": (24000, 29000)},
    {"name": "Bajaj 100L Water Heater", "brand": "Bajaj", "model_number": "MANTICNC", "category": "Appliances",
     "description": "Geyser 100L storage", "price_range": (22000, 28000)},
    {"name": "Seagate 2TB External Drive", "brand": "Seagate", "model_number": "STGX2000400", "category": "Storage",
     "description": "Portable HDD USB 3.0", "price_range": (5200, 6500)},
    {"name": "Crompton Ceiling Fan 1200mm", "brand": "Crompton", "model_number": "HIF1200", "category": "Home",
     "description": "High speed ceiling fan", "price_range": (1300, 2100)},
    {"name": "Havells LED Bulb 9W", "brand": "Havells", "model_number": "LED9W", "category": "Home",
     "description": "B22 cool day light", "price_range": (75, 140)},
    {"name": "Kent RO Water Purifier", "brand": "Kent", "model_number": "15993", "category": "Appliances",
     "description": "6L wall mount RO", "price_range": (11000, 14000)},
{"name": "Mi Band 8 Fitness Tracker", "brand": "Xiaomi", "model_number": "M2343B1", "category": "Wearables",
      "description": "Smart fitness band", "price_range": (1800, 2800)},
    # Medical equipment
    {"name": "Oxygen Cylinder 10L Medical Grade", "brand": "Phillips", "model_number": "OXY-10L", "category": "Medical",
      "description": "Portable oxygen cylinder with regulator and flow meter", "price_range": (4500, 5200)},
    {"name": "Oxygen Concentrator 5L Portable", "brand": "Nidek", "model_number": "NIDEK-5L", "category": "Medical",
      "description": "5L/min continuous flow, 93% purity, portable design", "price_range": (42000, 46000)},
    {"name": "Digital BP Monitor Upper Arm", "brand": "Omron", "model_number": "OMRON-BP786", "category": "Medical",
      "description": "Automatic blood pressure monitor with irregular heartbeat detection", "price_range": (1800, 2100)},
    {"name": "Pulse Oximeter Fingertip", "brand": "Dr. Trust", "model_number": "DRTRUST-OXY", "category": "Medical",
      "description": "SpO2 and pulse rate monitor, LED display", "price_range": (450, 550)},
    {"name": "Wheelchair Foldable Steel Frame", "brand": "Karma", "model_number": "KARMA-FOLD", "category": "Medical",
      "description": "Lightweight foldable wheelchair with detachable footrests", "price_range": (8500, 9500)},
    # Furniture
    {"name": "Ergonomic Office Chair Mesh Back", "brand": "Green Soul", "model_number": "GS-MESH", "category": "Furniture",
      "description": "Adjustable lumbar support, 3D armrests, tilt mechanism", "price_range": (7500, 8500)},
    {"name": "Executive Leather Office Chair", "brand": "Da Urban", "model_number": "DU-LEATHER", "category": "Furniture",
      "description": "High back, genuine leather, pneumatic height adjustment", "price_range": (12000, 13500)},
    {"name": "Study Chair with Writing Pad", "brand": "Nilkamal", "model_number": "NK-WRITING", "category": "Furniture",
      "description": "Stackable, foldable writing pad, durable plastic frame", "price_range": (950, 1150)},
    # Computers
    {"name": "Desktop Computer Intel i5 12th Gen 8GB/512GB", "brand": "Dell", "model_number": "OPTIPLEX-5000", "category": "Computers",
      "description": "OptiPlex SFF, Windows 11 Pro, 3-year warranty", "price_range": (38000, 41000)},
    {"name": "All-in-One PC Intel i7 12th Gen 16GB/1TB", "brand": "HP", "model_number": "HP-AIO-24", "category": "Computers",
      "description": "23.8 inch FHD display, Windows 11, wireless keyboard/mouse", "price_range": (68000, 72000)},
    {"name": "Mini PC Intel i5 11th Gen 8GB/256GB", "brand": "Intel NUC", "model_number": "NUC-I5-11", "category": "Computers",
      "description": "Compact form factor, VESA mountable, 4K support", "price_range": (28000, 30500)},
    {"name": "Workstation Tower Xeon W 32GB/1TB SSD", "brand": "Lenovo", "model_number": "THINKSTATION-P360", "category": "Computers",
      "description": "ThinkStation P360, NVIDIA T400, Linux ready", "price_range": (85000, 92000)},
    # Appliances
    {"name": "Industrial Air Cooler 50L", "brand": "Symphony", "model_number": "SYMPHONY-50L", "category": "Appliances",
      "description": "Honeycomb pads, 400 sq ft coverage, auto swing", "price_range": (8500, 9500)},
    {"name": "Water Purifier RO+UV 8L", "brand": "Kent", "model_number": "KENT-ROUV-8L", "category": "Appliances",
      "description": "RO+UV+UF, TDS controller, 20 LPH purification", "price_range": (12000, 13500)},
]

GEM_ONLY_PRODUCTS = [
    {"name": "GeM Exclusive Office Chair", "brand": "GeM", "model_number": "GEM-CHAIR-001", "category": "Office",
     "description": "Ergonomic office chair - GeM exclusive", "price_range": (8000, 12000)},
    {"name": "GeM Exclusive LED Panel Light", "brand": "GeM", "model_number": "GEM-LIGHT-001", "category": "Lighting",
     "description": "LED panel light for offices - GeM exclusive", "price_range": (1500, 2500)},
    {"name": "GeM Exclusive Water Dispenser", "brand": "GeM", "model_number": "GEM-WATER-001", "category": "Office",
     "description": "Hot/cold water dispenser - GeM exclusive", "price_range": (5000, 8000)},
]


def _seed_price(product_meta, price, marketplace):
    variation = (hash(product_meta["name"]) + hash(marketplace)) % 9 - 4
    return round(price * (1 + variation / 100.0), 2)


def run(db=None):
    owns_session = db is None
    session = db or SessionLocal()
    try:
        # Clear existing seed data (idempotent reseed)
        # Clear legacy mapping tables from migration FIRST (before ORM deletes due to FK constraints)
        # Use try/except since these tables may not exist on fresh databases
        for table in ["legacy_listing_mapping", "legacy_product_mapping", "legacy_marketplace_mapping"]:
            try:
                session.execute(text(f"DELETE FROM {table}"))
            except Exception:
                pass
        session.flush()
        
        # Clear existing seed data (idempotent reseed)
        session.query(PriceHistory).delete()
        session.query(Listing).delete()
        session.query(Product).delete()
        session.query(Marketplace).delete()

        marketplaces = {}
        for m in MARKETPLACES:
            mp = Marketplace(name=m["name"], slug=m["slug"], base_url=m["base_url"])
            session.add(mp)
            session.flush()
            marketplaces[m["name"]] = mp

        for i, p in enumerate(PRODUCTS):
            product = Product(
                name=p["name"],
                brand=p["brand"],
                model_number=p["model_number"],
                category=p["category"],
                description=p["description"],
            )
            session.add(product)
            session.flush()

            for mi, mname in enumerate([m["name"] for m in MARKETPLACES]):
                mp = marketplaces[mname]
                price = _seed_price(p, p["price_range"][0] + i, mname)
                listing = Listing(
                    product_id=product.id,
                    marketplace_id=mp.id,
                    title=p["name"],
                    url=f"{mp.base_url}/products/{p['model_number']}",
                    price=price,
                    currency="INR",
                    availability=(mi == 0 or i % 3 != 2),
                    rating=round(3.5 + (i % 10) / 10.0, 1),
                )
                session.add(listing)
                session.flush()
                # Two snapshots of price history per listing
                session.add(PriceHistory(listing_id=listing.id, price=price * 1.05))
                session.add(PriceHistory(listing_id=listing.id, price=price))

        # Create GeM-only products (only GeM marketplace listing)
        for i, p in enumerate(GEM_ONLY_PRODUCTS):
            product = Product(
                name=p["name"],
                brand=p["brand"],
                model_number=p["model_number"],
                category=p["category"],
                description=p["description"],
            )
            session.add(product)
            session.flush()

            # Only create GeM listing
            mp = marketplaces["GeM"]
            price = _seed_price(p, p["price_range"][0] + i, "GeM")
            listing = Listing(
                product_id=product.id,
                marketplace_id=mp.id,
                title=p["name"],
                url=f"{mp.base_url}/products/{p['model_number']}",
                price=price,
                currency="INR",
                availability=True,
                rating=round(4.0 + (i % 5) / 10.0, 1),
            )
            session.add(listing)
            session.flush()
            # Two snapshots of price history per listing
            session.add(PriceHistory(listing_id=listing.id, price=price * 1.05))
            session.add(PriceHistory(listing_id=listing.id, price=price))

        counts = {
            "marketplaces": session.query(Marketplace).count(),
            "products": session.query(Product).count(),
            "listings": session.query(Listing).count(),
            "price_history": session.query(PriceHistory).count(),
        }
        print(f"Seeded: {counts}")
        if owns_session:
            session.commit()
        return counts
    finally:
        if owns_session:
            session.close()


if __name__ == "__main__":
    run()