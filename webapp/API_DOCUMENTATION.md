# API Documentation

## Base URL
- Local: `http://localhost:8000`
- Production: `https://gem-price-backend.onrender.com`

---

## Endpoints

### Health Check
```
GET /health
```
**Response:**
```json
{"status": "ok"}
```

---

### Categories
```
GET /categories
```
**Response:**
```json
[
  {"category": "Appliances", "product_count": 6},
  {"category": "Audio", "product_count": 2},
  ...
]
```

---

### Search Products
```
GET /search?q={query}&category={category}
```
**Parameters:**
- `q` (optional): Search query string
- `category` (optional): Filter by category

**Response:**
```json
[
  {
    "id": 1,
    "name": "HP 15s Laptop",
    "brand": "HP",
    "model_number": "15s-fq2711TU",
    "category": "Laptops",
    "image_url": "https://...",
    "gem_price": 28880.0,
    "market_price": 27440.0,
    "savings": -1440.0,
    "savings_pct": -5.0,
    "match_confidence": 95.0,
    "last_updated": "2026-08-23T10:00:00Z"
  }
]
```

---

### Product Compare
```
GET /products/{product_id}/compare
```
**Response:**
```json
{
  "id": 1,
  "name": "HP 15s Laptop",
  "brand": "HP",
  "model_number": "15s-fq2711TU",
  "category": "Laptops",
  "description": "Intel Core i3...",
  "image_url": "https://...",
  "listings": [
    {
      "id": 1,
      "marketplace_id": 1,
      "marketplace_name": "GeM",
      "marketplace_slug": "gem",
      "title": "HP 15s Laptop",
      "url": "https://gem.gov.in/...",
      "image_url": "https://...",
      "price": 28880.0,
      "currency": "INR",
      "availability": true,
      "rating": 4.2,
      "scraped_at": "2026-08-23T10:00:00Z",
      "match_confidence": 95.0,
      "is_cheapest": false
    }
  ],
  "best_price": 27440.0,
  "best_marketplace": "Amazon",
  "matches": [],
  "gem_price": 28880.0,
  "market_best_price": 27440.0,
  "savings": -1440.0,
  "savings_pct": -5.0,
  "market_average": 28160.0,
  "match_confidence": 95.0,
  "last_updated": "2026-08-23T10:00:00Z"
}
```

---

### Price History
```
GET /products/{product_id}/price-history
```
**Response:**
```json
{
  "id": 1,
  "name": "HP 15s Laptop",
  "brand": "HP",
  "category": "Laptops",
  "series": [
    {
      "listing_id": 1,
      "marketplace_name": "GeM",
      "marketplace_slug": "gem",
      "points": [
        {"price": 28880.0, "recorded_at": "2026-08-23T10:00:00Z"},
        {"price": 27440.0, "recorded_at": "2026-08-22T10:00:00Z"}
      ]
    }
  ]
}
```

---

### Insights
```
GET /insights
```
**Response:**
```json
{
  "categories": [
    {"category": "Laptops", "products_with_gem": 16, "avg_savings": -1440.0, "total_savings": -23040.0},
    {"category": "Smartphones", "products_with_gem": 10, "avg_savings": 500.0, "total_savings": 5000.0}
  ],
  "overall": {"category": "overall", "products_with_gem": 186, "avg_savings": -120.5, "total_savings": -22410.0}
}
```

---

### Price Drop Alerts
```
GET /alerts
```
**Response:**
```json
[
  {
    "product_id": 1,
    "product_name": "HP 15s Laptop",
    "marketplace_name": "Amazon",
    "marketplace_slug": "amazon",
    "old_price": 28000.0,
    "new_price": 27440.0,
    "drop_amount": 560.0,
    "percent_drop": 2.0,
    "dropped_at": "2026-08-23T10:00:00Z"
  }
]
```

---

### Trending Products
```
GET /trending?limit=10
```
**Response:**
```json
[
  {
    "id": 1,
    "name": "HP 15s Laptop",
    "brand": "HP",
    "category": "Laptops",
    "image_url": "https://...",
    "best_price": 27440.0,
    "best_marketplace": "Amazon",
    "second_best_price": 28880.0,
    "savings": 1440.0,
    "savings_pct": 5.0
  }
]
```

---

## Error Responses

| Code | Description |
|------|-------------|
| 400 | Bad Request (invalid parameters) |
| 404 | Not Found (product/marketplace not found) |
| 422 | Validation Error |
| 500 | Internal Server Error |

---

## Rate Limiting
- Default: 60 requests/minute per IP
- Search: 30 requests/minute
- Scraper endpoints: 2 second delay between requests

---

## CORS
```
Access-Control-Allow-Origin: *
Access-Control-Allow-Methods: GET, POST, OPTIONS
Access-Control-Allow-Headers: *
```