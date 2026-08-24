import re
from datetime import datetime, timezone

from playwright.sync_api import sync_playwright

from scrapers.pipelines import MarketplacePipeline

USER_AGENT = "GeM-Price-Comparison-Project/1.0 (academic project; contact: student@example.com)"
BASE_URL = "https://www.snapdeal.com"
PAGE_LOAD_TIMEOUT_MS = 120000
WAIT_AFTER_LOAD_MS = 12000
RETRIES = 3

SEARCH_QUERIES = [
    ("laptop", "laptops"),
    ("smartphone", "smartphones"),
    ("television", "televisions"),
    ("headphone", "audio"),
    ("smartwatch", "wearables"),
]


def _parse_price(text: str | None) -> float | None:
    if not text:
        return None
    match = re.search(r"(\d[\d,]*)", text.replace("\u20b9", "").replace("Rs.", ""))
    if not match:
        return None
    try:
        return float(match.group(1).replace(",", ""))
    except ValueError:
        return None


class SnapdealScraper:
    def __init__(self):
        self.pipeline = MarketplacePipeline("snapdeal")

    def run(self) -> int:
        saved = 0
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(user_agent=USER_AGENT)
            for query, category in SEARCH_QUERIES:
                saved += self._scrape_search(page, query, category)
            browser.close()
        return saved

    def _scrape_search(self, page, query: str, category: str) -> int:
        saved = 0
        url = f"{BASE_URL}/search?keyword={query}"
        for attempt in range(1, RETRIES + 1):
            try:
                page.goto(url, timeout=PAGE_LOAD_TIMEOUT_MS, wait_until="domcontentloaded")
                page.wait_for_timeout(WAIT_AFTER_LOAD_MS)
                break
            except Exception as exc:  # noqa: BLE001
                print(f"[snapdeal] {category} attempt {attempt}/{RETRIES} failed: {exc}")
                if attempt == RETRIES:
                    return 0

        cards = page.locator("div.product-tuple-listing").all()
        print(f"[snapdeal] {category}: {len(cards)} cards")
        for card in cards:
            item = self._extract(card, category, url)
            if item is None:
                continue
            try:
                self.pipeline.process_item(item)
                saved += 1
            except Exception as exc:  # noqa: BLE001
                print(f"[snapdeal] {category}: save failed: {exc}")
        return saved

    @staticmethod
    def _extract(card, category: str, page_url: str) -> dict | None:
        try:
            link_node = card.locator("a.dp-widget-link").first
            link = link_node.get_attribute("href") or "" if link_node.count() else ""
            name_node = card.locator("p.product-title").first
            name = name_node.get_attribute("title") if name_node.count() else None
            if not name:
                name = name_node.inner_text().strip() if name_node.count() else None
            if not name:
                return None

            price_node = card.locator("span.product-price").first
            price_text = price_node.get_attribute("data-price") if price_node.count() else None
            price = _parse_price(price_text)
            if price is None:
                return None

            img = card.locator("img.product-image").first
            image_url = img.get_attribute("src") if img.count() else None

            is_live = (card.get_attribute("data-islive") or "true").lower() != "false"
            link = link.split("#", 1)[0] or f"{BASE_URL}/product/{name.replace(' ', '-')}/0"

            return {
                "name": name,
                "brand": None,
                "category": category,
                "url": link if link.startswith("http") else f"{BASE_URL}{link}",
                "price": price,
                "mrp": None,
                "available": is_live,
                "image_url": image_url,
                "scraped_at": datetime.now(timezone.utc).isoformat(),
                "source_page": page_url,
            }
        except Exception as exc:  # noqa: BLE001
            print(f"[snapdeal] extract failed: {exc}")
            return None


def run() -> int:
    return SnapdealScraper().run()


if __name__ == "__main__":
    count = run()
    print(f"[snapdeal] saved {count} listings")