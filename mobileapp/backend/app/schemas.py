from pydantic import BaseModel, ConfigDict


class MarketplaceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    slug: str
    base_url: str
    logo_url: str | None = None
    is_active: bool = True


class ListingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    marketplace_id: int
    marketplace_name: str
    marketplace_slug: str
    title: str | None = None
    url: str
    image_url: str | None = None
    price: float
    currency: str
    availability: bool
    rating: float | None = None
    scraped_at: str | None = None
    match_confidence: float | None = None
    is_cheapest: bool = False


class MatchedProductOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    brand: str | None
    model_number: str | None = None
    category: str
    description: str | None = None
    image_url: str | None = None
    confidence: float
    method: str
    best_price: float | None = None
    best_marketplace: str | None = None


class ProductCompareOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    brand: str | None
    model_number: str | None = None
    category: str
    description: str | None = None
    image_url: str | None = None
    listings: list[ListingOut]
    best_price: float | None = None
    best_marketplace: str | None = None
    matches: list[MatchedProductOut] = []

    # Website-compatible fields
    gem_price: float | None = None
    market_best_price: float | None = None
    savings: float | None = None
    savings_pct: float | None = None
    market_average: float | None = None
    match_confidence: float | None = None
    last_updated: str | None = None


class ProductSummaryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    brand: str | None
    model_number: str | None = None
    category: str
    image_url: str | None = None
    lowest_price: float | None = None
    marketplace_count: int

    # Website-compatible fields
    gem_price: float | None = None
    market_price: float | None = None
    savings: float | None = None
    savings_pct: float | None = None
    match_confidence: float | None = None
    last_updated: str | None = None


class CategoryOut(BaseModel):
    category: str
    product_count: int


class PricePointOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    price: float
    recorded_at: str


class PriceSeriesOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    listing_id: int
    marketplace_name: str
    marketplace_slug: str
    points: list[PricePointOut]


class PriceHistoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    brand: str | None
    category: str
    series: list[PriceSeriesOut]


class CategorySavingsOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    category: str
    products_with_gem: int
    avg_savings: float
    total_savings: float


class InsightsOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    categories: list[CategorySavingsOut]
    overall: CategorySavingsOut


class PriceDropAlertOut(BaseModel):
    product_id: int
    product_name: str
    marketplace_name: str
    marketplace_slug: str
    old_price: float
    new_price: float
    drop_amount: float
    percent_drop: float
    dropped_at: str


class TrendingProductOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    brand: str | None
    category: str
    image_url: str | None = None
    best_price: float | None = None
    best_marketplace: str | None = None
    second_best_price: float | None = None
    savings: float | None = None
    savings_pct: float | None = None


class HealthOut(BaseModel):
    status: str