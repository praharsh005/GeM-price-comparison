import re
from datetime import datetime, timezone

from playwright.sync_api import sync_playwright

from scrapers.pipelines import MarketplacePipeline

USER_AGENT = "GeM-Price-Comparison-Project/1.0 (academic project; contact: student@example.com)"
BASE_URL = "https://www.vijaysales.com"
PAGE_LOAD_TIMEOUT_MS = 90000
WAIT_AFTER_LOAD_MS = 7000

CATEGORY_URLS = {
    "laptops": f"{BASE_URL}/c/laptops-and-accessories",
    "smartphones": f"{BASE_URL}/c/smartphones",
    "televisions": f"{BASE_URL}/c/television-and-entertainment",
    "audio": f"{BASE_URL}/c/headphones-and-speakers",
    "wearables": f"{BASE_URL}/c/smart-watches",
}


def _parse_price(text: str | None) -> float | None:
    if not text:
        return None
    match = re.search(r"(\d[\d,]*)", text.replace("\u20b9", "").replace(",", ""))
    if not match:
        return None
    try:
        return float(match.group(1))
    except ValueError:
        return None


class VijaySalesScraper:
    def __init__(self):
        self.pipeline = MarketplacePipeline("vijaysales")

    def run(self) -> int:
        saved = 0
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(user_agent=USER_AGENT)
            for category, url in CATEGORY_URLS.items():
                saved += self._scrape_category(page, category, url)
            browser.close()
        return saved

    def _scrape_category(self, page, category: str, url: str) -> int:
        saved = 0
        try:
            page.goto(url, timeout=PAGE_LOAD_TIMEOUT_MS, wait_until="domcontentloaded")
            page.wait_for_timeout(WAIT_AFTER_LOAD_MS)
        except Exception as exc:  # noqa: BLE001
            print(f"[vijaysales] {category}: page load failed: {exc}")
            return 0

        cards = page.locator("a.product-card__link").all()
        print(f"[vijaysales] {category}: {len(cards)} cards")
        for card in cards:
            item = self._extract(card, category, url)
            if item is None:
                continue
            try:
                self.pipeline.process_item(item)
                saved += 1
            except Exception as exc:  # noqa: BLE001
                print(f"[vijaysales] {category}: save failed: {exc}")
        return saved

    @staticmethod
    def _extract(card, category: str, page_url: str) -> dict | None:
        try:
            link = card.get_attribute("href") or ""
            name_node = card.locator("div.product-name").first
            name = name_node.inner_text().strip() if name_node.count() else None
            price_node = card.locator("div.discountedPrice").first
            if not name or not price_node.count():
                return None

            price_text = price_node.get_attribute("data-price")
            price = _parse_price(price_text)
            if price is None:
                return None

            img = card.locator("img.product__image").first
            image_url = img.get_attribute("src") if img.count() else None

            in_stock = card.locator("[data-instock]").first
            available = True
            if in_stock.count():
                cls = (in_stock.get_attribute("class") or "").strip()
                available = "d-none" not in cls.split()

            return {
                "name": name,
                "brand": None,
                "category": category,
                "url": link if link.startswith("http") else f"{BASE_URL}{link}",
                "price": price,
                "mrp": None,
                "available": available,
                "image_url": image_url,
                "scraped_at": datetime.now(timezone.utc).isoformat(),
                "source_page": page_url,
            }
        except Exception as exc:  # noqa: BLE001
            print(f"[vijaysales] extract failed: {exc}")
            return None


def run() -> int:
    return VijaySalesScraper().run()


if __name__ == "__main__":
    count = run()
    print(f"[vijaysales] saved {count} listings")