"""네이버 쇼핑 기반 제품 맥락 조사 (페이지 크롤 대체)."""

from __future__ import annotations

from typing import Any

from naver_shopping import search_market_price


async def research_product_context(keyword: str) -> dict[str, Any]:
    """캠페인 제품/장소명으로 시장 맥락 수집."""
    if not keyword or not keyword.strip():
        return {"keyword": "", "context": "", "error": "keyword required"}

    market = await search_market_price(keyword.strip())
    if market.get("error"):
        return {
            "keyword": keyword,
            "context": "",
            "error": market["error"],
            "min_price": None,
            "max_price": None,
        }

    min_p = market.get("min_price")
    max_p = market.get("max_price")
    avg_p = market.get("avg_price")
    items = market.get("top_items") or market.get("items") or []

    snippets: list[str] = []
    if min_p and max_p:
        snippets.append(f"시장가 약 {min_p:,}~{max_p:,}원")
    elif avg_p:
        snippets.append(f"평균가 약 {avg_p:,}원")
    for item in items[:2]:
        name = item.get("title") or item.get("name") or ""
        price = item.get("price") or item.get("lprice")
        if name:
            snippets.append(f"{name[:40]}{'…' if len(name) > 40 else ''}" + (f" ({price:,}원)" if price else ""))

    context = " · ".join(snippets) if snippets else "시장 정보를 찾지 못했습니다."
    return {
        "keyword": keyword,
        "context": context,
        "min_price": min_p,
        "max_price": max_p,
        "avg_price": avg_p,
        "items_count": market.get("items_count"),
    }
