"""캠페인 추천 — easy_pick / by_need / urgent 통합."""

from __future__ import annotations

from typing import Any

from campaign_filters import (
    apply_filters,
    hot_campaigns,
    search_by_need,
    sort_by_popularity,
    urgent_campaigns,
)
from experience_value import enrich_campaign


def competition_ratio(campaign: dict[str, Any]) -> float:
    applicants = int(campaign.get("applicants") or 0)
    recruit = int(campaign.get("recruitCount") or 1)
    if recruit <= 0:
        return float(applicants)
    return applicants / recruit


def low_competition_key(campaign: dict[str, Any]) -> tuple[float, int, str]:
    """경쟁률 낮은 순 → D-day → id."""
    d_day = int(campaign.get("dDay") if campaign.get("dDay") is not None else 9999)
    return (competition_ratio(campaign), d_day, str(campaign.get("id") or ""))


def sort_by_low_competition(campaigns: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(campaigns, key=low_competition_key)


def easy_pick_campaigns(
    campaigns: list[dict[str, Any]],
    *,
    top_n: int = 5,
    filters: dict[str, Any] | None = None,
) -> tuple[list[dict[str, Any]], str]:
    """초보용: 경쟁 여유 + 체험가치 보통 이상 우선."""
    filtered = apply_filters(campaigns, filters)
    scored: list[tuple[float, dict[str, Any]]] = []
    for c in filtered:
        ratio = competition_ratio(c)
        if ratio > 3.0:
            continue
        row = enrich_campaign(c)
        exp = row.get("experience_value") or "정보없음"
        score = (3.0 - ratio) * 10
        if exp == "높음":
            score += 5
        elif exp == "보통":
            score += 2
        scored.append((score, c))
    if not scored:
        picked = sort_by_low_competition(filtered)[:top_n]
        return picked, "low_competition_fallback"
    scored.sort(key=lambda x: x[0], reverse=True)
    return [c for _, c in scored[:top_n]], "easy_pick"


def recommend_campaigns(
    campaigns: list[dict[str, Any]],
    *,
    mode: str = "by_need",
    need_text: str | None = None,
    top_n: int = 5,
    filters: dict[str, Any] | None = None,
    sort_by: str = "popular",
    max_dday: int = 1,
    region: str | None = None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """반환: (캠페인 목록, 메타)."""
    meta: dict[str, Any] = {"mode": mode, "sort_by": sort_by}

    if mode == "easy_pick":
        picked, sub = easy_pick_campaigns(campaigns, top_n=top_n, filters=filters)
        meta["sub_mode"] = sub
        return picked, meta

    if mode == "urgent":
        picked = urgent_campaigns(
            campaigns,
            top_n=top_n,
            max_dday=max_dday,
            filters=filters,
            region=region,
        )
        meta["max_dday"] = max_dday
        if region:
            meta["region"] = region
        return picked, meta

    if mode == "by_need" and need_text:
        matched, keywords, sub_mode, intent = search_by_need(
            campaigns, need_text, top_n=top_n * 2, filters=filters
        )
        meta.update({"keywords": keywords, "sub_mode": sub_mode, "intent": intent})
        picked = matched
    else:
        picked = hot_campaigns(campaigns, top_n=top_n * 2, filters=filters)
        meta["sub_mode"] = "popular_default"

    if sort_by == "low_competition":
        picked = sort_by_low_competition(picked)
    elif sort_by == "urgent":
        picked = sorted(
            picked,
            key=lambda c: (
                int(c.get("dDay") if c.get("dDay") is not None else 9999),
                -int(c.get("applicants") or 0),
            ),
        )
    else:
        picked = sort_by_popularity(picked)

    return picked[:top_n], meta
