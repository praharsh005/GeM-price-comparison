"""Accuracy tests for the RapidFuzz product-matching layer (Phase 6)."""

import logging

from app.matching import (
    MATCH_THRESHOLD,
    REVIEW_THRESHOLD,
    decide,
    normalize,
    score_pair,
)
from tests.matching_sample import FALSE_COUNT, SAMPLE, TRUE_COUNT

# The matcher should agree with the human labels on the large majority of
# the hand-labeled sample. Imperfect accuracy is expected and documented:
# the residual misses are near-threshold edge cases and brand-spelling
# aliases, which the review band is designed to catch.
MIN_ACCURACY = 0.85


def test_sample_is_balanced():
    assert len(SAMPLE) >= 30
    assert TRUE_COUNT >= 10
    assert FALSE_COUNT >= 10


def test_accuracy_on_hand_labeled_sample():
    correct = sum(1 for g, m, exp in SAMPLE if (score_pair(g, m) >= MATCH_THRESHOLD) == exp)
    accuracy = correct / len(SAMPLE)
    assert accuracy >= MIN_ACCURACY, f"accuracy {accuracy:.0%} < {MIN_ACCURACY:.0%}"


def test_thresholds_are_sane():
    assert 0 < MATCH_THRESHOLD < REVIEW_THRESHOLD <= 100


def test_decide_bands():
    is_match, band = decide(95)
    assert is_match and band == "high"
    is_match, band = decide(75)
    assert is_match and band == "medium"
    is_match, band = decide(40)
    assert not is_match and band == "low"


def test_exact_duplicate_scores_high():
    assert score_pair("Acer Aspire 5 Laptop", "Acer Aspire 5 Laptop") == 100.0


def test_brand_mismatch_is_capped():
    s = score_pair("Samsung VA Computer Monitor", "LG 27 inch VA Monitor")
    assert s <= 40


def test_capacity_mismatch_is_penalised():
    # Different LPM capacity -> not the same concentrator.
    s = score_pair("ORNATE Oxygen Concentrator 8 LPM", "Ornate 10 LPM Oxygen Concentrator")
    assert s <= 50


def test_normalize_strips_stopwords_and_abbreviations():
    a = normalize("SAMSUNG Vertical Alignment (VA) Computer Monitor")
    assert "computer" not in a.split()
    assert "va" in a.split()
    assert "monitor" not in a.split()
