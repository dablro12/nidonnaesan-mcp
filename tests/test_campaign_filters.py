from campaign_filters import apply_filters, extract_keywords, search_by_need


SAMPLE = [
    {
        "id": "1",
        "title": "아이 튜브 물놀이",
        "benefit": "튜브 제공",
        "category": "생활",
        "type": "배송형",
        "mediaType": "블로그",
        "platform": "체험뷰",
        "applicants": 5,
    },
    {
        "id": "2",
        "title": "강남 맛집",
        "benefit": "식사 5만원",
        "category": "맛집",
        "type": "방문형",
        "mediaType": "블로그",
        "platform": "레뷰",
        "applicants": 100,
    },
]


def test_search_by_need_keyword():
    matched, kws = search_by_need(SAMPLE, "아이 튜브 협찬", top_n=3)
    assert matched[0]["id"] == "1"
    assert "튜브" in kws


def test_filter_category():
    filtered = apply_filters(SAMPLE, {"category": "맛집"})
    assert len(filtered) == 1
    assert filtered[0]["category"] == "맛집"


def test_extract_keywords():
    kws = extract_keywords("아이가 놀 수 있는 튜브 협찬 찾아줘")
    assert "튜브" in kws
