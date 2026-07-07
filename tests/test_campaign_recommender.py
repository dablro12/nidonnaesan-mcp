"""campaign_recommender 단위 테스트."""

from campaign_recommender import competition_ratio, easy_pick_campaigns, recommend_campaigns, sort_by_low_competition


def _campaign(**kwargs):
    base = {
        "id": "1",
        "title": "[서울] 테스트 맛집",
        "category": "맛집",
        "applicants": 5,
        "recruitCount": 10,
        "dDay": 3,
        "benefit": "50,000원 상당 식사권",
        "mediaType": "블로그",
    }
    base.update(kwargs)
    return base


def test_competition_ratio() -> None:
    assert competition_ratio(_campaign(applicants=2, recruitCount=10)) == 0.2


def test_easy_pick_prefers_low_competition() -> None:
    campaigns = [
        _campaign(id="a", applicants=20, recruitCount=2),
        _campaign(id="b", applicants=1, recruitCount=10),
    ]
    picked, mode = easy_pick_campaigns(campaigns, top_n=1)
    assert mode == "easy_pick"
    assert picked[0]["id"] == "b"


def test_recommend_by_need_with_low_competition_sort() -> None:
    campaigns = [
        _campaign(id="a", title="강남 파스타", applicants=50, recruitCount=2),
        _campaign(id="b", title="강남 파스타", applicants=2, recruitCount=10),
    ]
    picked, meta = recommend_campaigns(
        campaigns,
        mode="by_need",
        need_text="강남 파스타",
        top_n=2,
        sort_by="low_competition",
    )
    assert meta["mode"] == "by_need"
    assert picked[0]["id"] == "b"


def test_sort_by_low_competition() -> None:
    campaigns = [
        _campaign(id="a", applicants=10, recruitCount=1),
        _campaign(id="b", applicants=1, recruitCount=10),
    ]
    sorted_c = sort_by_low_competition(campaigns)
    assert sorted_c[0]["id"] == "b"
