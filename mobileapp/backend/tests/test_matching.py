from app.matching import _score, normalize_name


def test_normalize_name_lowercases_and_strips():
    assert normalize_name("  Sony WH-CH520 Wireless Headphones! ") == "sony wh ch520 wireless headphones"


def test_score_same_product_different_listing_names():
    sim, cov = _score(
        normalize_name("Sony WH-CH520 Wireless Headphones"),
        normalize_name("SONY WH-CH520 Bluetooth Wireless On-Ear Headphones (Black)"),
    )
    assert sim >= 85
    assert cov >= 0.55


def test_score_equivalent_titles_high():
    sim, cov = _score(
        normalize_name("JBL Tune 510BT Wireless Headphones"),
        normalize_name("JBL Tune 510BT On Ear Wireless Headphones (Blue)"),
    )
    assert sim >= 85
    assert cov >= 0.55


def test_score_different_products_low():
    sim, cov = _score(
        normalize_name("Noise Alt Watch 1 Smartwatch AMOLED Display Bluetooth Calling"),
        normalize_name("T500 Smart Watch with Bluetooth Calling and Super AMOLED Display"),
    )
    assert sim < 85 or cov < 0.55


def test_score_no_common_core_tokens_zero():
    sim, cov = _score(
        normalize_name("JBL Flip 7 Portable Wireless Bluetooth Speaker"),
        normalize_name("Faymla Hongli Lithium Ion 1200mAH Rechargeable Cell Batteries"),
    )
    assert sim == 0.0 and cov == 0.0


def test_score_generic_tokens_alone_are_not_a_match():
    sim, cov = _score(
        normalize_name("Smart Watch Bluetooth Calling 4k UHD smart TV"),
        normalize_name("T500 Bluetooth Smartwatch Android Smartphone"),
    )
    assert sim < 85 or cov < 0.55
