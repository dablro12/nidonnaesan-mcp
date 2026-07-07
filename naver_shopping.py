"""네이버 쇼핑 검색 API."""

from __future__ import annotations

import os
from typing import Any

import httpx

NAVER_CLIENT_ID = os.getenv("NAVER_CLIENT_ID", "")
NAVER_CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET", "")


async def search_market_price(keyword: str, *, display: int = 10) -> dict[str, Any]:
    if not NAVER_CLIENT_ID or not NAVER_CLIENT_SECRET:
        return {
            "keyword": keyword,
            "min_price": None,
            "max_price": None,
            "avg_price": None,
            "items_count": 0,
            "error": "NAVER_CLIENT_ID/SECRET not configured",
        }

    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(
            "https://openapi.naver.com/v1/search/shop.json",
            params={"query": keyword, "display": display, "sort": "sim"},
            headers={
                "X-Naver-Client-Id": NAVER_CLIENT_ID,
                "X-Naver-Client-Secret": NAVER_CLIENT_SECRET,
            },
        )
        resp.raise_for_status()
        data = resp.json()

    items = data.get("items") or []
    prices = [int(item.get("lprice", 0)) for item in items if item.get("lprice")]
    if not prices:
        return {
            "keyword": keyword,
            "min_price": None,
            "max_price": None,
            "avg_price": None,
            "items_count": 0,
        }

    return {
        "keyword": keyword,
        "min_price": min(prices),
        "max_price": max(prices),
        "avg_price": round(sum(prices) / len(prices)),
        "items_count": len(prices),
        "sample_mall": items[0].get("mallName") if items else None,
    }
