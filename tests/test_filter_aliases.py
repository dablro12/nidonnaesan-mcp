"""영문 필터 별칭 정규화 테스트."""

from filter_aliases import filters_to_need_text, localize_filters, normalize_sort_by


def test_localize_english_region_category() -> None:
    out = localize_filters({"region": "Seoul", "category": "Western"})
    assert out["region"] == "서울"
    assert out["category"] == "맛집"


def test_localize_gangnam_cafe() -> None:
    out = localize_filters({"region": "Gangnam", "category": "Cafe"})
    assert out["region"] == "강남"
    assert out["category"] == "맛집"


def test_localize_accommodation_bupyeong() -> None:
    out = localize_filters({"region": "Bupyeong", "category": "Accommodation"})
    assert out["region"] == "부평"
    assert out["category"] == "숙박"


def test_normalize_sort_competition() -> None:
    assert normalize_sort_by("competition") == "low_competition"


def test_filters_to_need_text() -> None:
    text = filters_to_need_text({"region": "서울", "category": "맛집"})
    assert "서울" in text and "맛집" in text
