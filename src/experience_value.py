"""체험가치·경쟁률 라벨 계산."""

from __future__ import annotations

import re
from typing import Any

from campaign_geo import enrich_campaign_location, location_label

BENCHMARK_BY_MEDIA: dict[str, int] = {
    "블로그": 30_000,
    "인스타그램": 40_000,
    "인스타릴스": 50_000,
    "유튜브": 50_000,
    "유튜브쇼츠": 50_000,
    "블로그클립": 35_000,
}


def parse_benefit_value(benefit: str) -> int | None:
    if not benefit:
        return None
    text = benefit.replace(",", "")
    won = re.findall(r"(\d{1,3}(?:\d{3})*)\s*원", text)
    if won:
        return int(won[0])
    nums = re.findall(r"(\d{4,})", text)
    if nums:
        return int(nums[0])
    return None


def experience_value_label(provided: int | None, media_type: str) -> str:
    if provided is None:
        return "정보없음"
    benchmark = BENCHMARK_BY_MEDIA.get(media_type, 30_000)
    ratio = provided / benchmark
    if ratio >= 1.5:
        return "높음"
    if ratio >= 0.8:
        return "보통"
    return "낮음"


def competition_label(applicants: int, recruit_count: int) -> tuple[str, str]:
    if recruit_count <= 0:
        return "0/0 (0:1)", "보통"
    ratio = applicants / recruit_count
    label = f"{applicants}/{recruit_count} ({ratio:.1f}:1)"
    if ratio < 1.0:
        return label, "여유"
    if ratio <= 3.0:
        return label, "보통"
    return label, "치열"


def enrich_campaign(campaign: dict[str, Any], market_price: dict[str, Any] | None = None) -> dict[str, Any]:
    benefit = campaign.get("benefit") or ""
    media = campaign.get("mediaType") or "블로그"
    provided = parse_benefit_value(benefit)
    applicants = int(campaign.get("applicants") or 0)
    recruit = int(campaign.get("recruitCount") or 0)
    comp_str, comp_level = competition_label(applicants, recruit)

    row = {
        "id": campaign.get("id"),
        "platform": campaign.get("platform"),
        "title": campaign.get("title"),
        "category": campaign.get("category"),
        "type": campaign.get("type"),
        "mediaType": media,
        "benefit": benefit,
        "competition": comp_str,
        "competition_label": comp_level,
        "dDay": campaign.get("dDay"),
        "experience_value": experience_value_label(provided, media),
        "provided_value": provided,
        "apply_url": campaign.get("originalUrl"),
        "location_label": location_label(campaign),
        **enrich_campaign_location(campaign),
    }
    if market_price:
        row["market_price"] = (
            f"{market_price.get('min_price', 0):,}~{market_price.get('max_price', 0):,}원"
        )
    return row
