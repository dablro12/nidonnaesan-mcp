"""캠페인 필터링·니즈 검색."""

from __future__ import annotations

import re
from typing import Any

CATEGORY_KEYWORDS: dict[str, list[str]] = {
    "디지털": ["디지털", "IT", "전자", "스마트", "태블릿", "노트북", "이어폰", "가전"],
    "반려": ["반려", "펫", "강아지", "고양이", "애견", "반려동물"],
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
            result = [c for c in result if c.get(key) == val or (key == "mediaType" and val in (c.get(key) or ""))]

    return result


def extract_keywords(need_text: str) -> list[str]:
    stop = {"협찬", "체험단", "리뷰", "찾아", "찾아줘", "알려줘", "해줘", "있어", "없어"}
    tokens = re.findall(r"[가-힣a-zA-Z0-9]+", need_text)
    return [t for t in tokens if len(t) >= 2 and t not in stop]


def score_campaign(campaign: dict[str, Any], keywords: list[str]) -> float:
    if not keywords:
        return float(campaign.get("applicants") or 0)
    text = " ".join(
        str(campaign.get(k) or "")
        for k in ("title", "benefit", "category", "type", "platform")
    )
    hits = sum(1 for kw in keywords if kw in text)
    return hits * 10 + float(campaign.get("applicants") or 0) * 0.01


def search_by_need(
    campaigns: list[dict[str, Any]],
    need_text: str,
    *,
    top_n: int = 5,
    filters: dict[str, Any] | None = None,
) -> tuple[list[dict[str, Any]], list[str]]:
    filtered = apply_filters(campaigns, filters)
    keywords = extract_keywords(need_text)
    if keywords:
        scored = [(score_campaign(c, keywords), c) for c in filtered]
        scored = [(s, c) for s, c in scored if s > 0]
        scored.sort(key=lambda x: x[0], reverse=True)
        if scored:
            return [c for _, c in scored[:top_n]], keywords
    by_applicants = sorted(filtered, key=lambda c: c.get("applicants") or 0, reverse=True)
    return by_applicants[:top_n], keywords


def hot_campaigns(
    campaigns: list[dict[str, Any]],
    *,
    top_n: int = 5,
    filters: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    filtered = apply_filters(campaigns, filters)
    return sorted(filtered, key=lambda c: c.get("applicants") or 0, reverse=True)[:top_n]
