from aptitude_test import run_aptitude_test, resolve_aptitude_type


def test_food_explorer():
    result = run_aptitude_test(
        {
            "channel_type": "blog",
            "interest_category": "맛집",
            "region": "서울",
            "posting_frequency": "yes",
            "campaign_type_pref": "방문형",
            "sponsorship_experience": "no",
        }
    )
    assert result["aptitude_type"] == "food_explorer"
    assert result["filter_preset"]["category"] == "맛집"


def test_all_rounder_for_beginner():
    assert (
        resolve_aptitude_type(
            {"channel_type": "none", "sponsorship_experience": "no", "interest_category": "맛집"}
        )
        == "all_rounder"
    )
