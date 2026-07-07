"""신청 한마디 3문장 생성."""

from __future__ import annotations

from typing import Any

TONE_PREFIX = {
    "natural": "",
    "polite": "",
    "appeal": "",
}


def generate_comment(
    campaign: dict[str, Any],
    channel: dict[str, Any],
    *,
    tone: str = "natural",
) -> dict[str, str]:
    title = campaign.get("title") or "이 캠페인"
    category = campaign.get("category") or "체험"
    benefit = campaign.get("benefit") or ""
    blogger_type = channel.get("blogger_type") or "생활 블로거"
    blog_name = channel.get("blog_name") or "블로그"
    main_cat = (channel.get("main_categories") or ["생활"])[0]

    s1 = f"{blog_name}에서 {main_cat} 경험을 직접 기록하는 {blogger_type}입니다."
    s2 = f"평소 {main_cat} 콘텐츠를 꾸준히 올리고 있어 {title} 체험에 관심이 갑니다."
    if benefit and benefit != "상세페이지 참고":
        s2 = f"{title}의 {benefit} 혜택이 제 블로그 주제와 잘 맞아 신청합니다."
    s3 = "직접 촬영한 사진과 솔직한 사용/방문 후기를 꼼꼼히 작성하겠습니다."

    if tone == "polite":
        s3 = "정성껏 방문·체험 후 사진과 함께 솔직하고 꼼꼼한 후기를 남기겠습니다."
    elif tone == "appeal":
        s2 = f"{category} 리뷰 경험이 있어 {title} 캠페인에 잘 어울릴 것 같아 신청합니다."

    comment = f"{s1} {s2} {s3}"
    evidence = f"채널 주제({main_cat})와 캠페인 카테고리({category}) 일치"

    return {
        "comment": comment,
        "channel_evidence": evidence,
        "tips_reference": "selection_rate §1 — 신청 메시지 2~3문장",
    }
