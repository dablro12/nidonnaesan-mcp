"""캠페인 응답 빌드 — enrich + 표."""

from __future__ import annotations

from typing import Any

from campaign_formatter import campaigns_to_compact_markdown, campaigns_to_markdown
from experience_value import enrich_campaign
from price_enrichment import attach_price_labels


async def build_campaign_table(
    campaigns: list[dict[str, Any]],
    *,
    title: str,
    table_format: str = "compact",
    enrich_prices: bool = True,
) -> str:
    rows = [enrich_campaign(c) for c in campaigns]
    if enrich_prices:
        rows = await attach_price_labels(rows)
    if table_format == "compact":
        return campaigns_to_compact_markdown(rows, title=title)
    return campaigns_to_markdown(rows, title=title)
