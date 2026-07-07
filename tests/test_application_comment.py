"""application_comment v2 단위 테스트."""

from application_comment import generate_comment


def test_generate_comment_has_verification_footer() -> None:
    campaign = {"title": "[서울] 테스트 카페", "category": "맛집", "mediaType": "블로그"}
    channel = {
        "blog_name": "Needly Life",
        "blogger_type": "생활 블로거",
        "main_categories": ["맛집"],
    }
    result = generate_comment(campaign, channel, product_context="시장가 약 10,000~20,000원")
    assert "확인 기준:" in result["verification_footer"]
    assert len(result["comment"].split(".")) >= 2
    assert "Needly Life" in result["comment"]


def test_generate_comment_anonymous_channel() -> None:
    campaign = {"title": "[디지털] 텀블러 살균 건조기", "category": "생활", "mediaType": "블로그"}
    channel = {
        "anonymous": True,
        "blog_name": "리뷰어",
        "blogger_type": "IT 블로거",
        "main_categories": ["IT", "생활"],
    }
    result = generate_comment(campaign, channel)
    assert "리뷰어에서" not in result["comment"]
    assert "텀블러 살균 건조기" in result["comment"] or "신청합니다" in result["comment"]
