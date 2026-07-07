"""네이버 쇼핑 검색 API."""

from __future__ import annotations

import os
from typing import Any

import httpx

NAVER_CLIENT_ID = os.getenv("NAVER_CLIENT_ID", "")
NAVER_CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET", "")


def _naver_credentials() -> tuple[str, str]:
    return os.getenv("NAVER_CLIENT_ID", ""), os.getenv("NAVER_CLIENT_SECRET", "")


async def search_market_price(keyword: str, *, display: int = 10) -> dict[str, Any]:
    client_id, client_secret = _naver_credentials()
    if not client_id or not client_secret:
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
                "X-Naver-Client-Id": client_id,
                "X-Naver-Client-Secret": client_secret,
            },
        )
        if resp.status_code == 401:
            return {
                "keyword": keyword,
                "min_price": None,
                "max_price": None,
                "avg_price": None,
                "items_count": 0,
                "error": (
                    "NAVER API 401 (errorCode 024): 검색 API 미등록 또는 Client ID/Secret 불일치. "
                    "developers.naver.com → 내 애플리케이션 → API 설정 → '검색' 추가 후 확인"
                ),
            }
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
