"""캠페인 필터링·니즈 검색·인기순 정렬."""

from __future__ import annotations

import re
from typing import Any

from campaign_geo import expand_region_query, match_region, parse_need_intent

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
    for key in ("mediaType", "type", "platform", "category", "region", "max_dday"):
        val = filters.get(key)
        if val is not None and val != "전체" and val != "":
            out[key] = val
    return out


def _filter_by_region(campaigns: list[dict[str, Any]], region: str | None) -> list[dict[str, Any]]:
    if not region:
        return campaigns
    tokens = expand_region_query(region)
    return [c for c in campaigns if match_region(c, tokens)]


def _filter_by_max_dday(campaigns: list[dict[str, Any]], max_dday: int | None) -> list[dict[str, Any]]:
    if max_dday is None:
        return campaigns
    result = []
    for c in campaigns:
        d = c.get("dDay")
        if d is None:
            continue
        try:
            if 0 <= int(d) <= int(max_dday):
                result.append(c)
        except (TypeError, ValueError):
            continue
    return result


def apply_filters(campaigns: list[dict[str, Any]], filters: dict[str, Any] | None) -> list[dict[str, Any]]:
    f = normalize_filters(filters)
    if not f:
        return campaigns

    result = campaigns
    result = _filter_by_region(result, f.get("region"))
    result = _filter_by_max_dday(result, f.get("max_dday"))

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
    return parse_need_intent(need_text)["keywords"]


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


def urgency_key(campaign: dict[str, Any]) -> tuple[int, int, str]:
    """마감 임박순: D-day 오름차순 → 신청자 내림차순 → id."""
    d_day = int(campaign.get("dDay") if campaign.get("dDay") is not None else 9999)
    applicants = int(campaign.get("applicants") or 0)
    return (d_day, -applicants, str(campaign.get("id") or ""))


def sort_by_popularity(campaigns: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(campaigns, key=popularity_key)


def sort_by_urgency(campaigns: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(campaigns, key=urgency_key)


def search_by_need(
    campaigns: list[dict[str, Any]],
    need_text: str,
    *,
    top_n: int = 5,
    filters: dict[str, Any] | None = None,
) -> tuple[list[dict[str, Any]], list[str], str, dict[str, Any]]:
    """반환: (결과, 키워드, mode, intent)."""
    intent = parse_need_intent(need_text)
    merged_filters = {**(filters or {}), **intent.get("filters", {})}
    if intent.get("regions") and not merged_filters.get("region"):
        merged_filters["region"] = intent["regions"][0]
    if intent.get("max_dday") is not None and merged_filters.get("max_dday") is None:
        merged_filters["max_dday"] = intent["max_dday"]

    filtered = apply_filters(campaigns, merged_filters)
    keywords = intent["keywords"]
    region_tokens = intent.get("regions") or []

    if region_tokens:
        region_matched = [c for c in filtered if match_region(c, region_tokens)]
        if region_matched:
            filtered = region_matched

    if keywords:
        matched: list[tuple[int, dict[str, Any]]] = []
        for c in filtered:
            hits = keyword_hits(c, keywords)
            if hits > 0:
                score = hits * 100 + int(c.get("applicants") or 0)
                matched.append((score, c))
        if matched:
            matched.sort(key=lambda x: x[0], reverse=True)
            mode = "region_matched" if region_tokens else "matched"
            if intent.get("categories"):
                mode = "category_matched" if not region_tokens else "region_matched"
            return [c for _, c in matched[:top_n]], keywords, mode, intent

    if region_tokens and filtered:
        popular = sort_by_popularity(filtered)[:top_n]
        return popular, keywords, "region_matched", intent

    if intent.get("categories") and filtered:
        popular = sort_by_popularity(filtered)[:top_n]
        return popular, keywords, "category_matched", intent

    popular = sort_by_popularity(filtered)[:top_n]
    mode = "popular_fallback" if keywords or region_tokens else "popular_default"
    return popular, keywords, mode, intent


def hot_campaigns(
    campaigns: list[dict[str, Any]],
    *,
    top_n: int = 5,
    filters: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    filtered = apply_filters(campaigns, filters)
    return sort_by_popularity(filtered)[:top_n]


def urgent_campaigns(
    campaigns: list[dict[str, Any]],
    *,
    top_n: int = 5,
    max_dday: int = 1,
    filters: dict[str, Any] | None = None,
    region: str | None = None,
) -> list[dict[str, Any]]:
    merged = {**(filters or {})}
    if region:
        merged["region"] = region
    merged["max_dday"] = max_dday
    filtered = apply_filters(campaigns, merged)
    return sort_by_urgency(filtered)[:top_n]
