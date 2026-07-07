"""제품명·URL·ID로 캠페인 해석."""

from __future__ import annotations

import re
from typing import Any
from urllib.parse import urlparse

from campaign_client import fetch_all_campaigns, resolve_campaign_id


def _normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").strip().lower())


def _title_score(campaign: dict[str, Any], query: str) -> int:
    title = _normalize_text(campaign.get("title") or "")
    q = _normalize_text(query)
    if not title or not q:
        return 0
    if q in title:
        return 100 + len(q)
    tokens = [t for t in re.findall(r"[가-힣a-zA-Z0-9]+", q) if len(t) >= 2]
    return sum(10 for t in tokens if t in title)


def _extract_campaign_id_from_url(url: str) -> str | None:
    parsed = urlparse(url.strip())
    path = parsed.path or ""
    for pattern in (
        r"/campaigns?/(\d+)",
        r"/campaign/(\d+)",
        r"[?&]id=(\d+)",
        r"/(\d{5,})",
    ):
        m = re.search(pattern, f"{path}?{parsed.query}")
        if m:
            return m.group(1)
    return None


async def resolve_campaign(
    *,
    campaign_id: str | None = None,
    product_name: str | None = None,
    campaign_url: str | None = None,
) -> tuple[dict[str, Any] | None, str]:
    """반환: (캠페인, match_mode)."""
    if campaign_id and str(campaign_id).strip():
        found = await resolve_campaign_id(str(campaign_id).strip())
        return (found, "id") if found else (None, "id_not_found")

    if campaign_url and str(campaign_url).strip():
        url = str(campaign_url).strip()
        cid = _extract_campaign_id_from_url(url)
        if cid:
            found = await resolve_campaign_id(cid)
            if found:
                return found, "url_id"
        campaigns = await fetch_all_campaigns()
        for c in campaigns:
            orig = c.get("originalUrl") or ""
            if orig and (orig == url or url in orig or orig in url):
                return c, "url_exact"

    if product_name and str(product_name).strip():
        query = str(product_name).strip()
        campaigns = await fetch_all_campaigns()
        scored = [( _title_score(c, query), c) for c in campaigns]
        scored = [(s, c) for s, c in scored if s > 0]
        if scored:
            scored.sort(key=lambda x: x[0], reverse=True)
            return scored[0][1], "product_name"

    return None, "not_found"
