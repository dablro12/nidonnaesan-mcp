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
