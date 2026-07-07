"""channel_from_campaign 단위 테스트."""

from channel_profile import channel_from_campaign


def test_channel_from_campaign_digital() -> None:
    ch = channel_from_campaign({"title": "[디지털] 텀블러 살균 건조기", "category": "생활"})
    assert ch["anonymous"] is True
    assert ch["blogger_type"] == "IT 블로거"
    assert ch["campaign_product"] == "텀블러 살균 건조기"
