"""캠페인 필터링·니즈 검색·인기순 정렬."""

from __future__ import annotations

import re
from typing import Any

CATEGORY_KEYWORDS: dict[str, list[str]] = {
    "디지털": ["디지털", "IT", "전자", "스마트", "태블릿", "노트북", "이어폰", "가전"],
    "반려": ["반려", "펫", "강아지", "고양이", "애견", "반려동물"],
    "반려동물": ["반려", "펫", "강아지", "고양이", "애견", "반려동물"],
}

UI_TO_API_CATEGORY = {
    "맛집": "맛집",
    "뷰티": "뷰티",
    "숙박/여행": "숙박",
    "숙박": "숙박",
    "생활": "생활",
    "디지털": "생활",
    "반려동물": "생활",
    "전체": None,
}


def normalize_filters(filters: dict[str, Any] | None) -> dict[str, Any]:
    if not filters:
        return {}
    out: dict[str, Any] = {}
    for key in ("mediaType", "type", "platform", "category"):
        val = filters.get(key)
        if val and val != "전체":
            out[key] = val
    return out


def apply_filters(campaigns: list[dict[str, Any]], filters: dict[str, Any] | None) -> list[dict[str, Any]]:
    f = normalize_filters(filters)
    if not f:
        return campaigns

    result = campaigns
    category = f.get("category")
    if category:
        api_cat = UI_TO_API_CATEGORY.get(category, category)
        if api_cat:
            result = [c for c in result if c.get("category") == api_cat]
        if category in CATEGORY_KEYWORDS:
            kws = CATEGORY_KEYWORDS[category]
            result = [
                c
                for c in result
                if any(
                    kw in (c.get("title") or "") or kw in (c.get("benefit") or "")
                    for kw in kws
                )
            ]

    for key in ("mediaType", "type", "platform"):
        val = f.get(key)
        if val:
            result = [
                c
                for c in result
                if c.get(key) == val or (key == "mediaType" and val in (c.get(key) or ""))
            ]

    return result


def extract_keywords(need_text: str) -> list[str]:
    stop = {
        "협찬", "체험단", "리뷰", "찾아", "찾아줘", "알려줘", "해줘", "있어", "없어",
        "가지고", "오게", "해주", "보여", "추천", "검색", "관련", "가능", "원해",
    }
    tokens = re.findall(r"[가-힣a-zA-Z0-9]+", need_text)
    return [t for t in tokens if len(t) >= 2 and t not in stop]


def keyword_hits(campaign: dict[str, Any], keywords: list[str]) -> int:
    text = " ".join(
        str(campaign.get(k) or "")
        for k in ("title", "benefit", "category", "type", "platform", "address")
    )
    return sum(1 for kw in keywords if kw in text)


def popularity_key(campaign: dict[str, Any]) -> tuple[int, int, str]:
    """인기순: 신청자 수 내림차순 → D-day 오름차순(마감 임박) → id."""
    applicants = int(campaign.get("applicants") or 0)
    d_day = int(campaign.get("dDay") if campaign.get("dDay") is not None else 9999)
    return (-applicants, d_day, str(campaign.get("id") or ""))


def sort_by_popularity(campaigns: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(campaigns, key=popularity_key)


def search_by_need(
    campaigns: list[dict[str, Any]],
    need_text: str,
    *,
    top_n: int = 5,
    filters: dict[str, Any] | None = None,
) -> tuple[list[dict[str, Any]], list[str], str]:
    """반환: (결과, 키워드, mode) — mode는 matched|popular_fallback."""
    filtered = apply_filters(campaigns, filters)
    keywords = extract_keywords(need_text)

    if keywords:
        matched: list[tuple[int, dict[str, Any]]] = []
        for c in filtered:
            hits = keyword_hits(c, keywords)
            if hits > 0:
                score = hits * 100 + int(c.get("applicants") or 0)
                matched.append((score, c))
        if matched:
            matched.sort(key=lambda x: x[0], reverse=True)
            return [c for _, c in matched[:top_n]], keywords, "matched"

    popular = sort_by_popularity(filtered)[:top_n]
    mode = "popular_fallback" if keywords else "popular_default"
    return popular, keywords, mode


def hot_campaigns(
    campaigns: list[dict[str, Any]],
    *,
    top_n: int = 5,
    filters: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    filtered = apply_filters(campaigns, filters)
    return sort_by_popularity(filtered)[:top_n]
