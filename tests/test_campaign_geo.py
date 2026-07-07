from campaign_geo import extract_location_tags, location_label, match_region, parse_need_intent
from campaign_filters import urgent_campaigns


def test_parse_need_intent_seoul_restaurant():
    intent = parse_need_intent("서울쪽 레스토랑 협찬 추천해줘")
    assert "서울" in intent["regions"]
    assert "맛집" in intent["categories"]


def test_parse_need_intent_bupyeong():
    intent = parse_need_intent("부평 근처 숙박 체험단")
    assert any("부평" in r for r in intent["regions"])
    assert "숙박" in intent["categories"]


def test_title_region_tag():
    campaign = {
        "title": "[인천 부평] 레푸스 부평역점",
        "address": "인천 부평구 ...",
        "region": "지역",
    }
    tags = extract_location_tags(campaign)
    assert "부평" in tags
    assert "인천" in tags or "부평" in location_label(campaign)


def test_match_region():
    campaign = {"title": "[강남] 버드맨", "address": "서울 강남구", "region": "지역"}
    assert match_region(campaign, ["서울", "강남"])


def test_urgent_campaigns():
    sample = [
        {"id": "a", "dDay": 0, "applicants": 10, "title": "[서울] A"},
        {"id": "b", "dDay": 5, "applicants": 100, "title": "[서울] B"},
        {"id": "c", "dDay": 1, "applicants": 50, "title": "[서울] C"},
    ]
    result = urgent_campaigns(sample, top_n=2, max_dday=1)
    assert len(result) == 2
    assert result[0]["id"] == "a"
