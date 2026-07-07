from tips_loader import get_sponsorship_tip, load_tip, match_topic_by_query


def test_load_selection_rate_tip():
    tip = load_tip("selection_rate")
    assert tip["id"] == "selection_rate"
    assert len(tip.get("sections", [])) >= 5


def test_query_match_ad_disclosure():
    assert match_topic_by_query("광고 표기 어떻게 해") == "ad_disclosure"


def test_auto_recommend_for_none_experience():
    result = get_sponsorship_tip(
        topic="auto",
        profile={"experience_level": "none", "read_tip_ids": []},
    )
    assert result["tip_id"] == "selection_rate"
