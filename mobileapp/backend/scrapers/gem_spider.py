import re

import scrapy
from bs4 import BeautifulSoup

SEARCH_QUERIES = [
    ("laptop", "laptops"),
    ("smartphone", "smartphones"),
    ("television", "televisions"),
    ("headphone", "audio"),
    ("smartwatch", "wearables"),
]
SEARCH_URL = "https://gem.gov.in/searchresult/query/?q={query}"


class GemSpider(scrapy.Spider):
    name = "gem"

    custom_settings = {
        "ITEM_PIPELINES": {"scrapers.pipelines.GemPipeline": 300},
    }

    def start_requests(self):
        for query, category in SEARCH_QUERIES:
            yield scrapy.Request(
                SEARCH_URL.format(query=query),
                callback=self.parse_search,
                cb_kwargs={"category": category},
            )

    def parse_search(self, response, category):
        soup = BeautifulSoup(response.text, "html.parser")
        for anchor in soup.select("div.prosec a[href*='-cat.html']"):
            url = anchor.get("href")
            if url:
                yield scrapy.Request(
                    url,
                    callback=self.parse_product,
                    cb_kwargs={"category": category},
                )

    def parse_product(self, response, category):
        soup = BeautifulSoup(response.text, "html.parser")

        name_node = soup.select_one("h1[itemprop='name']")
        name = name_node.get_text(" ", strip=True) if name_node else None
        if not name:
            return

        brand_node = soup.select_one("h1 .brand")
        brand = brand_node.get_text(" ", strip=True) if brand_node else None
        if brand == "NA":
            brand = None

        price = self._parse_price(soup, "div.our_price")
        mrp = self._parse_price(soup, "div.list_price.strike")
        offer_price = self._parse_price(soup, "div.offer_price")

        stock_node = soup.select_one("div#in_stock strong.green")
        available = bool(stock_node) and "out of stock" not in stock_node.get_text(
            " ", strip=True
        ).lower()

        yield {
            "name": name,
            "brand": brand,
            "category": category,
            "url": response.url,
            "price": price or offer_price or mrp,
            "mrp": mrp,
            "available": available,
            "image_url": None,
        }

    @staticmethod
    def _parse_price(soup, selector: str) -> float | None:
        node = soup.select_one(selector)
        if not node:
            return None
        text = node.get_text(" ", strip=True)
        match = re.search(r"(\d[\d,]*\.\d{2})", text.replace("\u20b9", ""))
        if not match:
            match = re.search(r"(\d[\d,]*)", text)
        if not match:
            return None
        return float(match.group(1).replace(",", ""))