"""체험단 캠페인 API 클라이언트."""

from __future__ import annotations

import os
import time
from typing import Any

import httpx

CAMPAIGN_API_BASE = os.getenv(
    "CAMPAIGN_API_BASE",
    "https://api-on7fpupona-du.a.run.app",
)
_CACHE_TTL_SEC = int(os.getenv("CAMPAIGN_CACHE_TTL_SEC", "300"))
_cache: dict[str, Any] = {"campaigns": [], "fetched_at": 0.0}


async def fetch_all_campaigns(*, limit: int = 500, force: bool = False) -> list[dict[str, Any]]:
    now = time.monotonic()
    if (
        not force
        and _cache["campaigns"]
        and now - _cache["fetched_at"] < _CACHE_TTL_SEC
    ):
        return _cache["campaigns"]

    campaigns: list[dict[str, Any]] = []
    offset = 0
    page_limit = min(limit, 500)

    async with httpx.AsyncClient(timeout=15.0) as client:
        while len(campaigns) < limit:
            url = f"{CAMPAIGN_API_BASE}/campaigns"
            resp = await client.get(url, params={"limit": page_limit, "offset": offset})
            resp.raise_for_status()
            data = resp.json()
            batch = data.get("campaigns") or []
            if not batch:
                break
            campaigns.extend(batch)
            if len(batch) < page_limit:
                break
            offset += page_limit

    _cache["campaigns"] = campaigns[:limit]
    _cache["fetched_at"] = now
    return _cache["campaigns"]


async def fetch_campaign_by_id(campaign_id: str) -> dict[str, Any] | None:
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(f"{CAMPAIGN_API_BASE}/campaigns/{campaign_id}")
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
        data = resp.json()
        if isinstance(data, dict) and "campaign" in data:
            return data["campaign"]
        return data if isinstance(data, dict) else None


def clear_campaign_cache() -> None:
    _cache["campaigns"] = []
    _cache["fetched_at"] = 0.0
