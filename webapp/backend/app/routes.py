from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session, selectinload

from app.cache import SEARCH_PREFIX, SEARCH_TTL, get_json, set_json
from app.database import get_db
from app.models import Listing, Marketplace, PriceHistory, Product
from app.schemas import (
    CategoriesResponse,
    CategoryOut,
    CompareListingOut,
    ProductCompare,
    ProductSummary,
    SearchResponse,
)

router = APIRouter()


def _gem_listing(listings: list[Listing]) -> Listing | None:
    return next((l for l in listings if l.marketplace and l.marketplace.name == "GeM"), None)


def _market_prices(listings: list[Listing], gem: Listing | None = None) -> list[float]:
    """Prices from non-GeM listings (the market comparison set)."""
    return [
        l.current_price
        for l in listings
        if l.current_price is not None
        and l.current_price > 0
        and (gem is None or l.id != gem.id)
    ]


def _best_market_price(listings: list[Listing], gem: Listing | None = None) -> float | None:
    prices = _market_prices(listings, gem)
    return min(prices) if prices else None


def _market_average(listings: list[Listing], gem: Listing | None = None) -> float | None:
    prices = _market_prices(listings, gem)
    return round(sum(prices) / len(prices), 2) if prices else None


def _market_confidence(listings: list[Listing], gem: Listing | None = None) -> float | None:
    """Average match confidence across the non-GeM comparison listings."""
    confs = [
        l.match_confidence
        for l in listings
        if l.match_confidence is not None and (gem is None or l.id != gem.id)
    ]
    return round(sum(confs) / len(confs), 2) if confs else None


def _representative_image(listings: list[Listing], gem: Listing | None = None) -> str | None:
    """Prefer the GeM listing's image; otherwise the first listing that has one."""
    def has_image(l: Listing) -> bool:
        return bool(l.image_url and l.image_url.strip())

    if gem is not None and has_image(gem):
        return gem.image_url
    for l in listings:
        if has_image(l):
            return l.image_url
    return None


@router.get("/search", response_model=SearchResponse)
def search(q: str = "", category: str | None = None, limit: int = 20, db: Session = Depends(get_db)):
    cache_key = f"{SEARCH_PREFIX}{q.strip()}:{category or ''}:{limit}"
    cached = get_json(cache_key)
    if cached is not None:
        return SearchResponse.model_validate(cached)

    stmt = db.query(Product)
    if q.strip():
        needle = q.strip()
        like = f"%{needle}%"
        # substring match (fast path) OR fuzzy trigram similarity
        similarity = func.similarity(Product.name, needle)
        stmt = stmt.filter(
            Product.name.ilike(like)
            | Product.model_number.ilike(like)
            | (similarity >= 0.2)
        ).order_by(similarity.desc())
    if category:
        stmt = stmt.filter(Product.category == category)

    total = stmt.count()
    products = stmt.options(selectinload(Product.listings).selectinload(Listing.marketplace)).limit(limit).all()

    results = []
    for p in products:
        listings = p.listings
        gem = _gem_listing(listings)
        gem_price = gem.current_price if gem else None
        best = _best_market_price(listings, gem)
        savings = (best - gem_price) if (gem_price and best and best < gem_price) else None
        savings_pct = round((savings / gem_price) * 100, 2) if savings is not None and gem_price else None
        last_updated = max((l.scraped_at for l in listings), default=None)
        results.append(
            ProductSummary(
                id=p.id,
                name=p.name,
                brand=p.brand,
                model_number=p.model_number,
                category=p.category,
                image_url=_representative_image(listings, gem),
                gem_price=gem_price,
                market_price=best,
                savings=savings,
                savings_pct=savings_pct,
                match_confidence=_market_confidence(listings, gem),
                last_updated=last_updated,
            )
        )

    response = SearchResponse(query=q, total=total, results=results)
    set_json(cache_key, response.model_dump(mode="json"), ttl=SEARCH_TTL)
    return response


@router.get("/products/{product_id}/compare", response_model=ProductCompare)
def compare(product_id: int, db: Session = Depends(get_db)):
    product = (
        db.query(Product)
        .options(selectinload(Product.listings).selectinload(Listing.marketplace))
        .filter(Product.id == product_id)
        .first()
    )
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    listings = product.listings
    gem = _gem_listing(listings)
    gem_price = gem.current_price if gem else None
    best = _best_market_price(listings, gem)
    savings = (best - gem_price) if (gem_price and best and best < gem_price) else None
    savings_pct = round((savings / gem_price) * 100, 2) if savings is not None and gem_price else None

    market_avg = _market_average(listings, gem)
    last_updated = max((l.scraped_at for l in listings), default=None)

    compare_listings = []
    for l in listings:
        diff = (l.current_price - gem_price) if (l.current_price is not None and gem_price is not None) else None
        diff_pct = round((diff / gem_price) * 100, 2) if diff is not None and gem_price else None
        compare_listings.append(
            CompareListingOut(
                id=l.id,
                marketplace_id=l.marketplace_id,
                marketplace=l.marketplace,
                title=l.title,
                url=l.url,
                image_url=l.image_url,
                current_price=l.current_price,
                currency=l.currency,
                availability=l.availability,
                rating=l.rating,
                scraped_at=l.scraped_at,
                match_confidence=l.match_confidence,
                difference_from_gem=diff,
                difference_pct=diff_pct,
            )
        )

    # price history per listing
    histories = (
        db.query(PriceHistory)
        .filter(PriceHistory.listing_id.in_([l.id for l in listings]))
        .order_by(PriceHistory.recorded_at)
        .all()
    )
    price_history: dict[int, list] = {}
    for h in histories:
        price_history.setdefault(h.listing_id, []).append(h)

    return ProductCompare(
        id=product.id,
        name=product.name,
        brand=product.brand,
        model_number=product.model_number,
        category=product.category,
        description=product.description,
        image_url=_representative_image(listings, gem),
        match_confidence=_market_confidence(listings, gem),
        gem_price=gem_price,
        market_best_price=best,
        savings=savings,
        savings_pct=savings_pct,
        market_average=market_avg,
        last_updated=last_updated,
        listings=compare_listings,
        price_history={k: v for k, v in price_history.items()},
    )


@router.get("/categories", response_model=CategoriesResponse)
def categories(db: Session = Depends(get_db)):
    rows = (
        db.query(Product.category, func.count(Product.id))
        .group_by(Product.category)
        .order_by(Product.category)
        .all()
    )
    # average per-product savings % (positive = GeM cheaper than best market price)
    savings_by_cat: dict[str, list[float]] = {}
    products = (
        db.query(Product)
        .options(selectinload(Product.listings).selectinload(Listing.marketplace))
        .all()
    )
    for p in products:
        gem = _gem_listing(p.listings)
        best = _best_market_price(p.listings, gem)
        if not gem or not gem.current_price or not best:
            continue
        savings_by_cat.setdefault(p.category, []).append(
            round((gem.current_price - best) / gem.current_price * 100, 2)
        )

    cats = []
    for category, count in rows:
        per = savings_by_cat.get(category, [])
        avg = round(sum(per) / len(per), 2) if per else None
        cats.append(CategoryOut(name=category, product_count=count, avg_savings=avg))
    return CategoriesResponse(total=len(cats), categories=cats)
