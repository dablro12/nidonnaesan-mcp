"""네이버 쇼핑 기반 제품가격 라벨 보강."""

from __future__ import annotations

import re
from typing import Any

from experience_value import parse_benefit_value
from naver_shopping import search_market_price

_price_cache: dict[str, dict[str, Any]] = {}


def clean_search_keyword(title: str) -> str:
    text = re.sub(r"^\[[^\]]+\]\s*", "", title or "")
    text = re.sub(r"\[[^\]]+\]", "", text)
    text = re.sub(r"\([^)]*\)", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:60]


async def lookup_market_price(keyword: str) -> dict[str, Any]:
    key = keyword.strip()[:80]
    if not key:
        return {}
    if key in _price_cache:
        return _price_cache[key]
    result = await search_market_price(key)
    _price_cache[key] = result
    return result


async def attach_price_labels(
    rows: list[dict[str, Any]],
    *,
    max_lookups: int = 5,
) -> list[dict[str, Any]]:
    for i, row in enumerate(rows):
        provided = row.get("provided_value")
        benefit = row.get("benefit") or ""

        if provided:
            row["price_label"] = f"{provided:,}원"
            continue

        parsed = parse_benefit_value(benefit)
        if parsed:
            row["price_label"] = f"{parsed:,}원"
            row["provided_value"] = parsed
            continue

        if benefit and benefit not in ("상세페이지 참고", "-"):
            if i >= max_lookups:
                row["price_label"] = benefit[:28]
                continue

        if i < max_lookups:
            kw = clean_search_keyword(row.get("title") or "")
            if kw:
                market = await lookup_market_price(kw)
                if market.get("min_price"):
                    row["price_label"] = (
                        f"시장가 {market['min_price']:,}~{market['max_price']:,}원"
                    )
                    row["market_min"] = market["min_price"]
                    row["market_max"] = market["max_price"]
                    continue
                if market.get("error"):
                    row["price_notice"] = market["error"]

        row["price_label"] = benefit[:28] if benefit else "-"
    return rows
