"""Tests for the Flipkart scraper block-detection (Phase 6).

Flipkart blocks automated requests, so these tests validate the
documented-block behaviour without attempting to bypass the CAPTCHA.
"""

from app.scrapers.flipkart import BLOCK_SIGNATURES, CATEGORIES, check_blocked


class _FakeResponse:
    def __init__(self, status_code, text):
        self.status_code = status_code
        self.text = text


class _FakeSession:
    """A requests-like session that returns a canned response."""

    def __init__(self, response):
        self._response = response

    def get(self, url, timeout=None):
        return self._response


def test_categories_defined():
    assert set(CATEGORIES) == {"Laptops", "Monitors", "Printers", "Oxygen Concentrators"}


def test_block_signatures_present():
    assert "recaptcha" in BLOCK_SIGNATURES
    assert "captcha" in BLOCK_SIGNATURES


def test_detects_captcha_block():
    resp = _FakeResponse(200, "<html>Flipkart reCAPTCHA challenge</html>")
    result = check_blocked(_FakeSession(resp), "Laptops", "/search?q=laptop", rate_limit=0)
    assert result["blocked"] is True
    assert result["status"] == 200


def test_detects_http_403_block():
    resp = _FakeResponse(403, "<html>Forbidden</html>")
    result = check_blocked(_FakeSession(resp), "Laptops", "/search?q=laptop", rate_limit=0)
    assert result["blocked"] is True
    assert result["status"] == 403


def test_clean_page_reported_as_accessible():
    resp = _FakeResponse(200, "<html>Laptops - Buy Laptops Online at Best Price</html>")
    result = check_blocked(_FakeSession(resp), "Laptops", "/search?q=laptop", rate_limit=0)
    assert result["blocked"] is False
    assert result["category"] == "Laptops"
