"""Product matching across marketplaces using RapidFuzz.

Links listings from different marketplaces that describe the same (or
sufficiently similar) product onto a shared `products` row, computing a
0-100 confidence score. Matches below the accept threshold are not
accepted; medium-confidence matches are logged for manual review instead
of being silently accepted.

All functions here are pure/DB-agnostic except `find_best_gem_product`,
which queries the session for candidate GeM products.
"""

import logging
import re
import unicodedata

from rapidfuzz import fuzz

from app.models import Product

logger = logging.getLogger(__name__)

# Confidence bands (0-100).
MATCH_THRESHOLD = 70.0  # score >= this is accepted as a match
REVIEW_THRESHOLD = 85.0  # accepted match below this is logged for review

# Generic words carrying no product identity across sources.
_STOPWORDS = {
    "the", "a", "an", "and", "or", "with", "without", "for", "of", "to",
    "in", "on", "at", "computer", "laptop", "notebook", "monitor",
    "printer", "concentrator", "oxygen", "entry", "mid", "level", "new",
    "original", "warranty", "year", "years", "black", "grey", "color",
    "colour", "series", "model", "makes", "including", "etc", "andor",
    "single", "dual", "outlet", "power", "cable", "adapter", "keyboard",
    "screen", "display", "machine", "system", "units", "unit", "brand",
}

# Curated brand vocabulary used to penalise cross-brand matches.
_BRANDS = {
    "acer", "hp", "hewlett", "packard", "dell", "lenovo", "asus", "asus",
    "samsung", "canon", "brother", "epson", "cynix", "voltricq", "algoplus",
    "edler", "tvs", "electronics", "image", "king", "nimish", "aspino",
    "innovations", "taurus", "healthcare", "infi", "devilbiss", "medoxy",
    "niscoplast", "ornate", "sleep", "one", "evox", "logitech", "sony",
    "xiaomi", "mi", "oneplus", "jbl", "philips", "bosch", "seagate", "bajaj",
    "crompton", "havells", "kent", "ifb", "lenovo", "lg", "panasonic",
    "toshiba", "nokia", "realme", "oppo", "vivo", "anker",
}

# Model-like tokens worth rewarding when shared (cpu model, ram, size, etc.)
_MODEL_PATTERNS = [
    r"\bcore\s*i\d\b",        # core i3 / core i5
    r"\bryzen\s*\d\b",        # ryzen 3 / ryzen5
    r"\b\d{3,5}[a-z]\d?\b",   # 1245U, 1215U, 5625U
    r"\b\d+\s*(?:gb|tb)\b",   # 8GB, 16GB, 1TB
    r"\b\d{2}\s*inch\b",      # 24 inch
    r"\b\d+\s*lpm\b",         # 5 LPM
    r"\b\d+\s*mp\b",          # 24MP
    r"\b(?:va|ips)\b",        # panel type (VA / IPS)
]

_MODEL_RES = [re.compile(p, re.I) for p in _MODEL_PATTERNS]

# Synonym/abbreviation expansion applied during normalize() so that GeM's
# verbose phrasing and marketplace shorthand resolve to the same token.
_SYNONYMS = {
    "vertical": "va",
    "alignment": "va",
    "plane": "ips",
    "switching": "ips",
    "monochrome": "mono",
    "colour": "color",
    "lpm": "lpm",
}

_CAPACITY_RE = re.compile(r"(\d+(?:\.\d+)?)\s*(lpm|gb|tb|inch|kg|w|hz)\b", re.I)


def normalize(text):
    """Lowercase, expand abbreviations, strip punctuation/stopwords.

    Returns a canonical whitespace-separated token string used for
    similarity scoring.
    """
    if not text:
        return ""
    t = unicodedata.normalize("NFKD", str(text)).lower()
    t = t.replace("&", " and ")
    # expand "24 in" -> "24 inch" only when preceded by a number
    t = re.sub(r"(?<=\d)\s*in\b", " inch", t)
    t = re.sub(r"[^a-z0-9 ]", " ", t)
    words = []
    for w in t.split():
        w = _SYNONYMS.get(w, w)
        if w not in _STOPWORDS and len(w) > 1:
            words.append(w)
    return " ".join(sorted(set(words)))


def _capacity_tokens(text):
    """Set of (value, unit) capacity specs like (5, 'lpm') or (24, 'inch')."""
    if not text:
        return set()
    out = set()
    for m in _CAPACITY_RE.finditer(str(text).lower()):
        unit = m.group(2)
        if unit == "hz":
            continue  # refresh rate is not a product-size spec
        try:
            out.add((float(m.group(1)), unit))
        except ValueError:
            continue
    return out


def extract_brand(text):
    """Return a canonical brand token if one is recognized, else None."""
    if not text:
        return None
    toks = str(text).lower().split()
    for tok in toks:
        if tok in _BRANDS:
            return tok
    return None


def _model_tokens(text):
    found = set()
    for rx in _MODEL_RES:
        found.update(m.group(0).replace(" ", "") for m in rx.finditer(text))
    return found


def score_pair(gem_title, market_title):
    """Return a 0-100 match confidence between a GeM and a market title."""
    a = normalize(gem_title)
    b = normalize(market_title)
    if not a or not b:
        return 0.0

    set_a, set_b = set(a.split()), set(b.split())
    shared = set_a & set_b
    union = set_a | set_b
    coverage = len(shared) / len(union) if union else 0.0

    # token_set_ratio over-scores tiny overlaps (e.g. brand-only), so
    # dampen it by how much of the combined vocabulary is actually shared.
    base = fuzz.token_set_ratio(a, b)
    base = base * (0.5 + 0.5 * coverage)
    score = max(base, fuzz.WRatio(a, b))

    # reward shared model tokens (cpu model, capacity, size, lpm, panel type)
    shared_models = _model_tokens(a) & _model_tokens(b)
    if shared_models:
        score = min(100.0, score + 15)
    elif len(shared) < 2:
        # a single shared token (e.g. brand only) is too thin a basis
        score = min(score, 55.0)

    # penalise mismatched numeric capacities/sizes (e.g. 5 LPM vs 8 LPM)
    cap_a = _capacity_tokens(gem_title)
    cap_b = _capacity_tokens(market_title)
    if cap_a and cap_b and cap_a != cap_b:
        score = min(score, 50.0)

    # penalise a known brand mismatch
    brand_a = extract_brand(gem_title)
    brand_b = extract_brand(market_title)
    if brand_a and brand_b and brand_a != brand_b:
        score = min(score, 40.0)

    return round(score, 2)


def find_best_gem_product(db, title, category=None):
    """Find the best candidate GeM product for a market listing.

    Returns ``(product, score)`` where product may be None when no
    candidate scores high enough to be worth considering.
    """
    best, best_score = None, 0.0
    q = db.query(Product)
    if category:
        q = q.filter(Product.category == category)
    for p in q.all():
        score = score_pair(p.name, title)
        if score > best_score:
            best, best_score = p, score
    return best, best_score


def decide(score):
    """Turn a raw score into (is_match, band) using the thresholds."""
    if score >= MATCH_THRESHOLD:
        return True, ("high" if score >= REVIEW_THRESHOLD else "medium")
    return False, "low"


def log_review(item_title, candidate, score):
    """Log a low/medium-confidence outcome so it can be manually reviewed."""
    band = decide(score)[1]
    logger.warning(
        "Matching review (%s): %r ~ %r (score %.1f)",
        band,
        item_title,
        candidate,
        score,
    )
