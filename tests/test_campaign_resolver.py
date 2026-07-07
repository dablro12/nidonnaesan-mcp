"""campaign_resolver 단위 테스트."""

import pytest

from campaign_resolver import _extract_campaign_id_from_url, _title_score


def test_extract_campaign_id_from_url() -> None:
    assert _extract_campaign_id_from_url("https://example.com/campaign/12345") == "12345"
    assert _extract_campaign_id_from_url("https://example.com/campaigns?id=98765") == "98765"


def test_title_score_partial_match() -> None:
    campaign = {"title": "[서울] 강남 파스타 맛집 체험"}
    assert _title_score(campaign, "강남 파스타") > 0


@pytest.mark.asyncio
async def test_resolve_campaign_by_product_name() -> None:
    from campaign_resolver import resolve_campaign

    campaign, mode = await resolve_campaign(product_name="존재하지않는제품xyz123")
    assert campaign is None
    assert mode == "not_found"
