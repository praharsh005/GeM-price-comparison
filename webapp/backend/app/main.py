from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

import itertools

from app.cache import search_cache_get, search_cache_set
from app.database import get_db
from app.models import Listing, Marketplace, PriceHistory, Product, ProductMatch
from app.schemas import (
    CategoryOut,
    CategorySavingsOut,
    HealthOut,
    InsightsOut,
    ListingOut,
    MatchedProductOut,
    PriceDropAlertOut,
    PriceHistoryOut,
    PricePointOut,
    PriceSeriesOut,
    ProductCompareOut,
    ProductSummaryOut,
    TrendingProductOut,
)


def _escape_like(text: str) -> str:
    return text.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def _gem_listing(listings: list[Listing]) -> Listing | None:
    return next((l for l in listings if l.marketplace and l.marketplace.slug == "gem"), None)


def _market_prices(listings: list[Listing], gem: Listing | None = None) -> list[float]:
    return [
        l.price
        for l in listings
        if l.price is not None and l.price > 0 and (gem is None or l.id != gem.id)
    ]


def _best_market_price(listings: list[Listing], gem: Listing | None = None) -> float | None:
    prices = _market_prices(listings, gem)
    return float(min(prices)) if prices else None


def _market_average(listings: list[Listing], gem: Listing | None = None) -> float | None:
    prices = _market_prices(listings, gem)
    return round(sum(float(p) for p in prices) / len(prices), 2) if prices else None


def _market_confidence(listings: list[Listing], gem: Listing | None = None) -> float | None:
    confs = [
        l.match_confidence
        for l in listings
        if l.match_confidence is not None and (gem is None or l.id != gem.id)
    ]
    return round(sum(float(c) for c in confs) / len(confs), 2) if confs else None


def _representative_image(listings: list[Listing], gem: Listing | None = None) -> str | None:
    def has_image(l: Listing) -> bool:
        return bool(l.image_url and l.image_url.strip())

    if gem is not None and has_image(gem):
        return gem.image_url
    for l in listings:
        if has_image(l):
            return l.image_url
    return None


def _compute_savings(gem_price: float | None, market_price: float | None) -> tuple[float | None, float | None]:
    if gem_price and market_price:
        gp = float(gem_price)
        mp = float(market_price)
        if mp < gp:
            savings = mp - gp
            savings_pct = round((savings / gp) * 100, 2)
            return savings, savings_pct
    return None, None


def _last_updated(listings: list[Listing]) -> str | None:
    dates = [l.scraped_at for l in listings if l.scraped_at]
    if not dates:
        return None
    return max(dates).isoformat()


app = FastAPI(title="GeM Price Comparison API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthOut)
def health():
    return HealthOut(status="ok")


@app.get("/categories", response_model=list[CategoryOut])
def categories(db: Session = Depends(get_db)):
    rows = db.execute(
        select(Product.category, func.count(Product.id))
        .group_by(Product.category)
        .order_by(Product.category)
    ).all()
    return [CategoryOut(category=cat, product_count=count) for cat, count in rows]


@app.get("/search", response_model=list[ProductSummaryOut])
def search(
    q: str = Query("", min_length=0, max_length=200),
    category: str | None = None,
    db: Session = Depends(get_db),
):
    cached = search_cache_get(q, category)
    if cached is not None:
        return cached

    # Load products with listings for gem/market price computation
    stmt = (
        select(Product)
        .options(selectinload(Product.listings).selectinload(Listing.marketplace))
        .where(Product.category == category if category else True)
    )
    if q.strip():
        stmt = stmt.where(Product.name.ilike(f"%{_escape_like(q.strip())}%", escape="\\"))
    if category:
        stmt = stmt.where(Product.category == category)

    products = db.execute(stmt).scalars().all()

    results = []
    for p in products:
        listings = p.listings
        gem = _gem_listing(listings)
        gem_price = float(gem.price) if gem and gem.price else None
        best = _best_market_price(listings, gem)
        savings, savings_pct = _compute_savings(gem_price, best)
        last_upd = _last_updated(listings)

        results.append(
            ProductSummaryOut(
                id=p.id,
                name=p.name,
                brand=p.brand,
                model_number=p.model_number,
                category=p.category,
                image_url=_representative_image(listings, gem),
                lowest_price=gem_price,
                marketplace_count=len(listings),
                gem_price=gem_price,
                market_price=best,
                savings=savings,
                savings_pct=savings_pct,
                match_confidence=_market_confidence(listings, gem),
                last_updated=last_upd,
            )
        )

    search_cache_set(q, category, [r.model_dump() for r in results])
    return results


@app.get("/products/{product_id}/compare", response_model=ProductCompareOut)
def compare(product_id: int, db: Session = Depends(get_db)):
    product = db.get(Product, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    rows = db.execute(
        select(
            Listing.id.label("listing_id"),
            Listing.marketplace_id,
            Listing.price,
            Listing.currency,
            Listing.url,
            Listing.title,
            Listing.image_url,
            Listing.availability,
            Listing.rating,
            Listing.scraped_at,
            Listing.match_confidence,
            Marketplace.name.label("marketplace_name"),
            Marketplace.slug.label("marketplace_slug"),
        )
        .join(Marketplace, Marketplace.id == Listing.marketplace_id)
        .where(Listing.product_id == product_id)
        .order_by(Listing.price)
    ).all()

    listings = [
        ListingOut(
            id=r.listing_id,
            marketplace_id=r.marketplace_id,
            marketplace_name=r.marketplace_name,
            marketplace_slug=r.marketplace_slug,
            title=r.title,
            url=r.url,
            image_url=r.image_url,
            price=float(r.price),
            currency=r.currency,
            availability=r.availability,
            rating=float(r.rating) if r.rating else None,
            scraped_at=r.scraped_at.isoformat() if r.scraped_at else None,
            match_confidence=float(r.match_confidence) if r.match_confidence else None,
            is_cheapest=r.availability and (r.price == rows[0].price),
        )
        for r in rows
    ]

    gem = _gem_listing(product.listings)
    gem_price = float(gem.price) if gem and gem.price else None
    best = _best_market_price(product.listings, gem)
    savings, savings_pct = _compute_savings(gem_price, best)
    market_avg = _market_average(product.listings, gem)
    last_upd = _last_updated(product.listings)
    match_conf = _market_confidence(product.listings, gem)

    rows_a = db.execute(
        select(ProductMatch, Product)
        .join(Product, Product.id == ProductMatch.product_a_id)
        .where(ProductMatch.product_b_id == product_id)
    ).all()
    rows_b = db.execute(
        select(ProductMatch, Product)
        .join(Product, Product.id == ProductMatch.product_b_id)
        .where(ProductMatch.product_a_id == product_id)
    ).all()
    match_rows = sorted(rows_a + rows_b, key=lambda r: r[0].confidence, reverse=True)

    matches: list[MatchedProductOut] = []
    for match, counterpart in match_rows:
        price_row = db.execute(
            select(func.min(Listing.price), Marketplace.name)
            .join(Marketplace, Marketplace.id == Listing.marketplace_id)
            .where(
                Listing.product_id == counterpart.id,
                Listing.availability.is_(True),
            )
            .group_by(Marketplace.id)
            .order_by(func.min(Listing.price))
        ).first()
        matches.append(
            MatchedProductOut(
                id=counterpart.id,
                name=counterpart.name,
                brand=counterpart.brand,
                model_number=counterpart.model_number,
                category=counterpart.category,
                description=counterpart.description,
                image_url=counterpart.image_url,
                confidence=float(match.confidence),
                method=match.method,
                best_price=float(price_row[0]) if price_row else None,
                best_marketplace=price_row[1] if price_row else None,
            )
        )

    return ProductCompareOut(
        id=product.id,
        name=product.name,
        brand=product.brand,
        model_number=product.model_number,
        category=product.category,
        description=product.description,
        image_url=_representative_image(product.listings, gem),
        listings=listings,
        best_price=gem_price,
        best_marketplace=gem.marketplace.name if gem else None,
        matches=matches,
        gem_price=gem_price,
        market_best_price=best,
        savings=savings,
        savings_pct=savings_pct,
        market_average=market_avg,
        match_confidence=match_conf,
        last_updated=last_upd,
    )


@app.get("/products/{product_id}/price-history", response_model=PriceHistoryOut)
def price_history(product_id: int, db: Session = Depends(get_db)):
    product = db.get(Product, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    rows = db.execute(
        select(
            Listing.id.label("listing_id"),
            Marketplace.name.label("marketplace_name"),
            Marketplace.slug.label("marketplace_slug"),
            PriceHistory.price,
            PriceHistory.recorded_at,
        )
        .join(Listing, Listing.id == PriceHistory.listing_id)
        .join(Marketplace, Marketplace.id == Listing.marketplace_id)
        .where(Listing.product_id == product_id)
        .order_by(Marketplace.name, PriceHistory.recorded_at)
    ).all()

    series: dict[int, dict] = {}
    for r in rows:
        entry = series.setdefault(
            r.listing_id,
            {
                "listing_id": r.listing_id,
                "marketplace_name": r.marketplace_name,
                "marketplace_slug": r.marketplace_slug,
                "points": [],
            },
        )
        entry["points"].append(
            PricePointOut(price=float(r.price), recorded_at=r.recorded_at.isoformat())
        )

    return PriceHistoryOut(
        id=product.id,
        name=product.name,
        brand=product.brand,
        category=product.category,
        series=[PriceSeriesOut(**s) for s in series.values()],
    )


@app.get("/insights", response_model=InsightsOut)
def insights(db: Session = Depends(get_db)):
    gem_id = db.scalar(select(Marketplace.id).where(Marketplace.slug == "gem"))

    gem_prices = db.execute(
        select(
            Product.id,
            Product.category,
            func.min(Listing.price).label("gem_price"),
        )
        .join(Listing, Listing.product_id == Product.id)
        .where(Listing.marketplace_id == gem_id, Listing.availability.is_(True))
        .group_by(Product.id, Product.category)
    ).all()

    best_others = db.execute(
        select(
            Listing.product_id,
            func.min(Listing.price).label("best_other"),
        )
        .where(
            Listing.marketplace_id != gem_id,
            Listing.availability.is_(True),
        )
        .group_by(Listing.product_id)
    ).all()
    best_other_by_product = {pid: price for pid, price in best_others}

    totals: dict[str, dict] = {}
    for pid, category, gem_price in gem_prices:
        stats = totals.setdefault(
            category,
            {"products_with_gem": 0, "savings_sum": 0.0},
        )
        stats["products_with_gem"] += 1
        other = best_other_by_product.get(pid)
        if other is not None and other > gem_price:
            stats["savings_sum"] += float(other) - float(gem_price)

    categories = []
    for category, stats in sorted(totals.items()):
        avg = stats["savings_sum"] / stats["products_with_gem"] if stats["products_with_gem"] else 0.0
        categories.append(
            CategorySavingsOut(
                category=category,
                products_with_gem=stats["products_with_gem"],
                avg_savings=round(avg, 2),
                total_savings=round(stats["savings_sum"], 2),
            )
        )

    n = sum(c.products_with_gem for c in categories)
    total = sum(c.total_savings for c in categories)
    overall = CategorySavingsOut(
        category="overall",
        products_with_gem=n,
        avg_savings=round(total / n, 2) if n else 0.0,
        total_savings=round(total, 2),
    )
    return InsightsOut(categories=categories, overall=overall)


@app.get("/alerts", response_model=list[PriceDropAlertOut])
def alerts(db: Session = Depends(get_db)):
    rows = db.execute(
        select(
            Listing.id.label("listing_id"),
            Listing.product_id,
            Product.name.label("product_name"),
            Marketplace.name.label("marketplace_name"),
            Marketplace.slug.label("marketplace_slug"),
            PriceHistory.price,
            PriceHistory.recorded_at,
        )
        .join(Listing, Listing.id == PriceHistory.listing_id)
        .join(Product, Product.id == Listing.product_id)
        .join(Marketplace, Marketplace.id == Listing.marketplace_id)
        .order_by(Listing.id, PriceHistory.recorded_at)
    ).all()

    drops: list[PriceDropAlertOut] = []
    for listing_id, group in itertools.groupby(rows, key=lambda r: r.listing_id):
        points = list(group)
        if len(points) < 2:
            continue
        last, prev = points[-1], points[-2]
        if last.price >= prev.price:
            continue
        drop = float(prev.price - last.price)
        drops.append(
            PriceDropAlertOut(
                product_id=last.product_id,
                product_name=last.product_name,
                marketplace_name=last.marketplace_name,
                marketplace_slug=last.marketplace_slug,
                old_price=float(prev.price),
                new_price=float(last.price),
                drop_amount=round(drop, 2),
                percent_drop=round(drop / float(prev.price) * 100, 2),
                dropped_at=last.recorded_at.isoformat(),
            )
        )

    drops.sort(key=lambda d: d.dropped_at, reverse=True)
    return drops[:30]


@app.get("/trending", response_model=list[TrendingProductOut])
def trending(db: Session = Depends(get_db), limit: int = Query(10, ge=1, le=50)):
    rows = db.execute(
        select(
            Product.id,
            Product.name,
            Product.brand,
            Product.category,
            Product.image_url,
            Marketplace.name.label("marketplace_name"),
            Listing.price,
        )
        .join(Listing, Listing.product_id == Product.id)
        .join(Marketplace, Marketplace.id == Listing.marketplace_id)
        .where(Listing.availability.is_(True))
        .order_by(Product.id, Listing.price)
    ).all()

    per_product: dict[int, dict] = {}
    for r in rows:
        entry = per_product.setdefault(
            r.id,
            {
                "name": r.name,
                "brand": r.brand,
                "category": r.category,
                "image_url": r.image_url,
                "by_marketplace": {},
            },
        )
        prices = entry["by_marketplace"]
        prices[r.marketplace_name] = min(
            prices.get(r.marketplace_name, r.price), r.price
        )

    result: list[TrendingProductOut] = []
    for pid, p in per_product.items():
        ordered = sorted(p["by_marketplace"].values())
        if len(ordered) < 2:
            continue
        best, second = ordered[0], ordered[1]
        savings = float(second) - float(best)
        if savings <= 0:
            continue
        best_name = min(p["by_marketplace"], key=p["by_marketplace"].get)
        result.append(
            TrendingProductOut(
                id=pid,
                name=p["name"],
                brand=p["brand"],
                category=p["category"],
                image_url=p["image_url"],
                best_price=float(best),
                best_marketplace=best_name,
                second_best_price=float(second),
                savings=round(savings, 2),
                savings_pct=round(savings / float(best) * 100, 2),
            )
        )

    result.sort(key=lambda t: t.savings, reverse=True)
    return result[:limit]