#!/usr/bin/env python3
"""PlayMCP 실사용 시나리오 검증 — 쉬움→어려움 10개."""

from __future__ import annotations

import asyncio
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))
load_dotenv(ROOT / ".env")

from campaign_client import fetch_all_campaigns, resolve_campaign_id
from campaign_output import build_campaign_table
from campaign_recommender import recommend_campaigns
from naver_shopping import search_market_price
from nidonnaesan_server import (
    compare_product_market_price,
    get_campaign_recommendations,
    get_sponsorship_tips,
    get_today_hot_campaigns,
    get_urgent_campaigns,
    search_campaigns_by_need,
)


@dataclass
class Scenario:
    level: str
    name: str
    fn: Callable
    kwargs: dict[str, Any]
    checks: list[str]


def _has_table(text: str) -> bool:
    return "| 협찬 제품명 |" in text or "| 플랫폼 |" in text


def _has_price(text: str) -> bool:
    return bool(re.search(r"\d{1,3}(?:,\d{3})+원|시장가", text))


async def run_scenario(sc: Scenario) -> dict[str, Any]:
    try:
        result = await sc.fn(**sc.kwargs) if asyncio.iscoroutinefunction(sc.fn) else sc.fn(**sc.kwargs)
        text = result if isinstance(result, str) else json.dumps(result, ensure_ascii=False)
        failed = [c for c in sc.checks if c == "table" and not _has_table(text)]
        failed += [c for c in sc.checks if c == "price" and not _has_price(text)]
        failed += [c for c in sc.checks if c == "naver" and "네이버 시장가" not in text and "min_price" not in text]
        status = "OK" if not failed else "FAIL"
        return {
            "level": sc.level,
            "name": sc.name,
            "status": status,
            "failed_checks": failed,
            "preview": text[:350].replace("\n", " "),
        }
    except Exception as exc:
        return {
            "level": sc.level,
            "name": sc.name,
            "status": "FAIL",
            "error": str(exc),
        }


async def build_scenarios() -> list[Scenario]:
    camps = await fetch_all_campaigns()
    sample = camps[0]
    sample_id = sample["id"]
    sample_title = sample.get("title", "")

    return [
        Scenario("easy", "초보 팁", get_sponsorship_tips, {"topic": "auto"}, []),
        Scenario(
            "easy",
            "경쟁률 낮은 추천",
            get_campaign_recommendations,
            {"mode": "easy_pick", "top_n": 5, "table_format": "compact"},
            ["table", "price"],
        ),
        Scenario(
            "easy",
            "인기 협찬",
            get_today_hot_campaigns,
            {"top_n": 5},
            ["table", "price"],
        ),
        Scenario(
            "medium",
            "서울 레스토랑 need_text",
            get_campaign_recommendations,
            {"mode": "by_need", "need_text": "서울쪽 레스토랑 협찬 추천해줘", "top_n": 5},
            ["table"],
        ),
        Scenario(
            "medium",
            "마감 임박",
            get_urgent_campaigns,
            {"max_dday": 1, "top_n": 5},
            ["table"],
        ),
        Scenario(
            "medium",
            "부평 숙박",
            search_campaigns_by_need,
            {"need_text": "부평 근처 숙박 체험단", "top_n": 5},
            ["table"],
        ),
        Scenario(
            "medium",
            "뷰티 배송 low_comp",
            get_campaign_recommendations,
            {
                "mode": "by_need",
                "need_text": "뷰티 배송형 협찬",
                "sort_by": "low_competition",
                "top_n": 5,
            },
            ["table"],
        ),
        Scenario(
            "hard",
            "시장가 비교 keyword",
            compare_product_market_price,
            {"keyword": "다이슨 선풍기"},
            ["naver"],
        ),
        Scenario(
            "hard",
            "시장가 비교 numeric id",
            compare_product_market_price,
            {"campaign_id": str(sample_id).split("-")[-1]},
            ["naver"],
        ),
        Scenario(
            "hard",
            "플랫폼 다양성",
            get_today_hot_campaigns,
            {"top_n": 5},
            ["table"],
        ),
    ]


async def main() -> None:
    scenarios = await build_scenarios()
    results = [await run_scenario(s) for s in scenarios]

    # platform diversity via hot_campaigns
    from campaign_filters import hot_campaigns

    camps = await fetch_all_campaigns()
    hot = hot_campaigns(camps, top_n=5, diversify=True)
    unique_platforms = len({c.get("platform") for c in hot})

    summary = {
        "scenarios": results,
        "platform_diversity_unique": unique_platforms,
        "passed": sum(1 for r in results if r["status"] == "OK"),
        "total": len(results),
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if summary["passed"] < summary["total"] or unique_platforms < 2:
        raise SystemExit(1)


if __name__ == "__main__":
    asyncio.run(main())
