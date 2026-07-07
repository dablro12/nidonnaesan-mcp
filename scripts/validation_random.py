#!/usr/bin/env python3
"""랜덤 샘플 기반 MCP 툴 검증."""

from __future__ import annotations

import asyncio
import json
import random
import sys
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
load_dotenv(ROOT / ".env")

from campaign_client import fetch_all_campaigns, fetch_campaign_by_id, get_campaign_meta
from campaign_filters import hot_campaigns, search_by_need
from experience_value import enrich_campaign
from naver_shopping import search_market_price
from tips_loader import get_sponsorship_tip, load_tip

SAMPLE_QUERIES = [
    "맛집 협찬", "뷰티 릴스", "아이 튜브", "강남 카페", "숙박 펜션",
    "강아지 간식", "이어폰", "존재하지않는키워드xyz", "디저트", "캠핑",
]
TIP_TOPICS = ["selection_rate", "blog_index", "platform", "ad_disclosure", "posting_omission"]


async def main() -> None:
    random.seed(42)
    results: dict[str, list] = {"checks": []}

    campaigns = await fetch_all_campaigns()
    meta = get_campaign_meta()
    results["campaign_pool"] = meta.get("total") or len(campaigns)

    # 1. 랜덤 캠페인 ID 링크 조회 10건
    sample_ids = [c["id"] for c in random.sample(campaigns, min(10, len(campaigns)))]
    link_ok = 0
    for cid in sample_ids:
        c = await fetch_campaign_by_id(cid)
        ok = bool(c and c.get("originalUrl"))
        link_ok += int(ok)
        results["checks"].append({"tool": "get_campaign_link", "id": cid, "ok": ok, "url": (c or {}).get("originalUrl")})
    results["get_campaign_link_random"] = f"{link_ok}/10"

    # 2. 인기순 TOP 검증
    hot = hot_campaigns(campaigns, top_n=5)
    applicants = [c.get("applicants", 0) for c in hot]
    results["hot_top5_applicants"] = applicants
    results["hot_sorted"] = applicants == sorted(applicants, reverse=True)

    # 3. 랜덤 니즈 검색 10건
    for q in random.sample(SAMPLE_QUERIES, 10):
        matched, kws, mode, _intent = search_by_need(campaigns, q, top_n=5)
        results["checks"].append({
            "tool": "search_campaigns_by_need",
            "query": q,
            "keywords": kws,
            "mode": mode,
            "count": len(matched),
            "top_title": matched[0]["title"] if matched else None,
        })

    # 4. 네이버 쇼핑 3건
    for kw in random.sample(["립스틱", "무선 이어폰", "강아지 사료"], 3):
        m = await search_market_price(kw)
        results["checks"].append({
            "tool": "compare_product_market_price",
            "keyword": kw,
            "min": m.get("min_price"),
            "max": m.get("max_price"),
            "error": m.get("error"),
        })

    # 5. 팁 markdown 소스 5건
    for topic in TIP_TOPICS:
        tip = load_tip(topic)
        results["checks"].append({
            "tool": "get_sponsorship_tips",
            "topic": topic,
            "source": tip.get("source"),
            "content_len": len(tip.get("sections_markdown") or ""),
        })

    # 6. 랜덤 캠페인 체험가치
    for c in random.sample(campaigns, 3):
        row = enrich_campaign(c)
        results["checks"].append({
            "tool": "enrich_campaign",
            "title": c["title"][:40],
            "experience_value": row["experience_value"],
            "competition": row["competition"],
        })

    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
