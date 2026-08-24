"""Flipkart search scraper (documented-blocked).

Flipkart.com serves a reCAPTCHA challenge to unauthenticated automated
requests: even `robots.txt` returns HTTP 403 and the search page returns
`Flipkart reCAPTCHA` instead of product content.

Per the project's scraping ethics rules we must not bypass CAPTCHAs,
logins, or other access controls, so this scraper does NOT attempt to
defeat the challenge. Instead it makes a single honest, rate-limited
request, verifies that the block is present, and reports it clearly so
the limitation is documented rather than hidden.

Run directly: `python -m app.scrapers.flipkart`
"""

import argparse
import logging
import time

import requests
from sqlalchemy import select

from app.config import settings
from app.database import SessionLocal
from app.models import Marketplace

logger = logging.getLogger(__name__)

BASE_URL = "https://www.flipkart.com"
FLIPKART_NAME = "Flipkart"

HEADERS = {
    "User-Agent": (
        "GeMPriceIntelligenceResearchBot/0.1 "
        "(educational price comparison project; contact: student@example.com)"
    ),
    "Accept-Language": "en-IN,en;q=0.9",
}

# Category name -> search path.
CATEGORIES = {
    "Laptops": "/search?q=laptop",
    "Monitors": "/search?q=computer+monitor",
    "Printers": "/search?q=printer",
    "Oxygen Concentrators": "/search?q=oxygen+concentrator",
}

BLOCK_SIGNATURES = ("captcha", "recaptcha", "unusual traffic", "verify you are")


def check_blocked(session, category, path, rate_limit):
    """Probe one category URL and classify the response.

    Returns a dict describing the outcome:
    ``{"category": ..., "blocked": bool, "status": int, "detail": str}``
    """
    logger.info("Probing Flipkart %s", path)
    url = BASE_URL + path
    detail = "unexpected error"
    blocked = True
    status = None
    try:
        resp = session.get(url, timeout=30)
        status = resp.status_code
        low = resp.text.lower()
        if status == 200 and not any(s in low for s in BLOCK_SIGNATURES):
            blocked = False
            detail = "search page returned product content"
        elif any(s in low for s in BLOCK_SIGNATURES):
            detail = f"reCAPTCHA/bot challenge detected (HTTP {status})"
        else:
            detail = f"access denied (HTTP {status})"
    except requests.RequestException as exc:
        detail = f"request failed: {type(exc).__name__}"
    logger.info("Rate-limited: sleeping %.1fs", rate_limit)
    time.sleep(rate_limit)
    return {"category": category, "blocked": blocked, "status": status, "detail": detail}


def run():
    """Probe Flipkart and report the block status. Returns probe results."""
    db = SessionLocal()
    try:
        flipkart = db.scalar(select(Marketplace).where(Marketplace.name == FLIPKART_NAME))
        if flipkart is None:
            flipkart = Marketplace(name=FLIPKART_NAME, base_url=BASE_URL)
            db.add(flipkart)
            db.commit()

        session = requests.Session()
        session.headers.update(HEADERS)
        results = []
        for category, path in CATEGORIES.items():
            result = check_blocked(session, category, path, settings.scraper_rate_limit)
            results.append(result)
            logger.warning(
                "Flipkart %s: %s -> %s",
                result["category"],
                "BLOCKED" if result["blocked"] else "accessible",
                result["detail"],
            )
        return results
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Probe Flipkart accessibility")
    parser.parse_args()
    logging.basicConfig(level=logging.INFO)
    for res in run():
        print(res)
