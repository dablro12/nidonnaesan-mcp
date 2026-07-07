"""신청 한마디 3문장 생성 — skill 기반 v2."""

from __future__ import annotations

import re
from typing import Any

BLOGGER_BY_CATEGORY: dict[str, str] = {
    "맛집": "생활 블로거",
    "숙박": "여행 블로거",
    "뷰티": "뷰티 블로거",
    "생활": "생활 블로거",
}

MOTIVE_SCENES: dict[str, list[str]] = {
    "맛집": [
        "퇴근 후 들를 만한 곳을 찾다가",
        "주말 약속 장소를 고르다가",
        "근처에서 혼밥하기 좋은 곳을 찾다가",
    ],
    "숙박": [
        "서울 근교에서 쉬고 싶은 일정을 짜다가",
        "여행 일정에 맞는 숙소를 찾다가",
        "가족과 함께 머물 만한 곳을 알아보다가",
    ],
    "뷰티": [
        "요즘 피부 루틴을 정리하다가",
        "계절 바뀜에 맞춰 케어 제품을 찾다가",
        "평소 관심 있던 뷰티 아이템을 비교하다가",
    ],
    "생활": [
        "일상에 필요한 제품을 직접 써보고 싶어서",
        "요즘 생활 루틴을 바꾸다가",
        "실사용 후기가 필요한 제품을 찾다가",
    ],
}


def _clean_title(title: str) -> str:
    return re.sub(r"^\[[^\]]+\]\s*", "", title or "").strip() or "이 캠페인"


def _infer_blogger_type(campaign: dict[str, Any], channel: dict[str, Any]) -> str:
    if channel.get("blogger_type"):
        return channel["blogger_type"]
    category = campaign.get("category") or "생활"
    return BLOGGER_BY_CATEGORY.get(category, "생활 블로거")


def _pick_motive(category: str, title: str, product_context: str | None) -> str:
    scenes = MOTIVE_SCENES.get(category, MOTIVE_SCENES["생활"])
    base = scenes[hash(title) % len(scenes)]
    if product_context and "시장가" in product_context:
        return f"{base} {title}의 실사용 후기가 궁금해"
    if category == "맛집":
        return f"{base} {title} 메뉴와 분위기가 궁금해"
    if category == "숙박":
        return f"{base} {title}을 직접 머물며 경험해보고 싶어"
    return f"{base} {title}을 제 생활 속에서 직접 써보고 싶어"


def _review_promise(campaign: dict[str, Any], category: str) -> str:
    media = campaign.get("mediaType") or "블로그"
    if category == "맛집":
        return "메뉴 선택, 좌석 분위기, 방문 동선, 사진과 영상까지 담아 솔직한 후기로 작성하겠습니다."
    if category == "숙박":
        return "객실·주변 동선·실제 머문 느낌을 사진과 함께 꼼꼼히 기록하겠습니다."
    if "릴스" in media or "인스타" in media:
        return "실사용·방문 장면을 사진·영상으로 담아 솔직하고 꼼꼼한 후기를 남기겠습니다."
    return "직접 촬영한 사진과 솔직한 사용·방문 후기를 꼼꼼히 작성하겠습니다."


def generate_comment(
    campaign: dict[str, Any],
    channel: dict[str, Any],
    *,
    tone: str = "natural",
    product_context: str | None = None,
) -> dict[str, str]:
    title = _clean_title(campaign.get("title") or "")
    category = campaign.get("category") or "생활"
    blog_name = channel.get("blog_name") or "블로그"
    main_cat = (channel.get("main_categories") or ["생활"])[0]
    blogger_type = _infer_blogger_type(campaign, channel)

    s1 = f"{blog_name}에서 {main_cat} 경험을 직접 기록하는 {blogger_type}입니다."

    motive = _pick_motive(category, title, product_context)
    s2 = f"{motive} 신청합니다."
    if tone == "appeal":
        s2 = f"{category} 리뷰 경험이 있어 {title} 캠페인에 잘 어울릴 것 같아 신청합니다."
    elif tone == "polite":
        s2 = f"평소 {main_cat} 콘텐츠를 꾸준히 올리고 있어 {title} 체험에 관심이 있어 신청드립니다."

    s3 = _review_promise(campaign, category)
    if tone == "polite":
        s3 = "정성껏 방문·체험 후 사진과 함께 솔직하고 꼼꼼한 후기를 남기겠습니다."

    comment = f"{s1} {s2} {s3}"
    evidence_parts = [f"채널 주제({main_cat})", f"캠페인 카테고리({category})"]
    if product_context:
        evidence_parts.append(f"제품 맥락({product_context[:60]})")
    evidence = " · ".join(evidence_parts)

    footer_checks = [
        "신청 동기가 캠페인·채널에 맞는지",
        "3문장·자연스러운 톤",
        "과장·허위 수치 없음",
    ]
    if product_context:
        footer_checks.append("제품 맥락 반영")

    return {
        "comment": comment,
        "channel_evidence": evidence,
        "tips_reference": "selection_rate §1 — 신청 메시지 2~3문장",
        "verification_footer": "확인 기준: " + " · ".join(footer_checks),
    }
