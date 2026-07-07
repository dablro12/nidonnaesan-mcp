"""nidonnaesan(니돈내산) MCP Server — PlayMCP Streamable HTTP."""

from __future__ import annotations

import json
import os
from typing import Any

from dotenv import load_dotenv

load_dotenv()

from mcp.server.fastmcp import FastMCP

from application_comment import generate_comment
from aptitude_test import run_aptitude_test
from campaign_client import fetch_all_campaigns, fetch_campaign_by_id
from campaign_filters import apply_filters, hot_campaigns, search_by_need
from campaign_formatter import campaigns_to_markdown, dict_to_markdown
from channel_profile import analyze_channel
from experience_value import enrich_campaign, parse_benefit_value
from mcp_tool_result import install_tool_error_wrapping
from naver_shopping import search_market_price
from profile_store import filter_defaults, get_profile, set_profile
from tips_loader import get_sponsorship_tip

MCP_HOST = os.getenv("MCP_HOST", "0.0.0.0")
MCP_PORT = int(os.getenv("MCP_PORT", "8000"))
SERVICE = "nidonnaesan(니돈내산)"
MCP_ID = "nidonnaesan"

mcp = FastMCP(MCP_ID, host=MCP_HOST, port=MCP_PORT)

READ_ONLY = {
    "readOnlyHint": True,
    "destructiveHint": False,
    "openWorldHint": True,
    "idempotentHint": True,
}

WRITE_PROFILE = {
    "readOnlyHint": False,
    "destructiveHint": False,
    "openWorldHint": False,
    "idempotentHint": True,
}


def _resolve_filters(
    filters: dict[str, Any] | None,
    profile: dict[str, Any] | None,
) -> dict[str, Any]:
    if filters:
        return filters
    return filter_defaults(profile or {})


def _parse_json_arg(val: str | dict[str, Any] | None) -> dict[str, Any] | None:
    if val is None:
        return None
    if isinstance(val, dict):
        return val
    if isinstance(val, str) and val.strip():
        return json.loads(val)
    return None


@mcp.tool(
    annotations={**READ_ONLY, "title": "Today's Hot Campaigns"},
)
async def get_today_hot_campaigns(
    top_n: int = 5,
    filters: dict[str, Any] | None = None,
    profile: dict[str, Any] | None = None,
) -> str:
    f"""Returns today's most popular sponsorship campaigns from {SERVICE} sorted by applicants."""
    stored = get_profile(profile_fallback=profile) or profile
    effective_filters = _resolve_filters(filters, stored)
    campaigns = await fetch_all_campaigns()
    hot = hot_campaigns(campaigns, top_n=top_n, filters=effective_filters)
    rows = [enrich_campaign(c) for c in hot]
    return campaigns_to_markdown(rows, title=f"오늘의 인기 협찬 TOP {top_n}")


@mcp.tool(
    annotations={**READ_ONLY, "title": "Search Campaigns by Need"},
)
async def search_campaigns_by_need(
    need_text: str,
    top_n: int = 5,
    filters: dict[str, Any] | None = None,
    profile: dict[str, Any] | None = None,
) -> str:
    f"""Searches sponsorship campaigns by natural-language need from {SERVICE}."""
    stored = get_profile(profile_fallback=profile) or profile
    effective_filters = _resolve_filters(filters, stored)
    campaigns = await fetch_all_campaigns()
    matched, keywords, mode = search_by_need(
        campaigns, need_text, top_n=top_n, filters=effective_filters
    )
    rows = [enrich_campaign(c) for c in matched]
    header = f"니즈 탐색: {need_text}"
    if keywords:
        header += f" (키워드: {', '.join(keywords)})"
    if mode == "popular_fallback":
        header += " — 키워드 매칭 없음, 인기순(신청자 수)으로 표시"
    return campaigns_to_markdown(rows, title=header)


@mcp.tool(
    annotations={**READ_ONLY, "title": "Compare Market Price"},
)
async def compare_product_market_price(
    campaign_id: str | None = None,
    keyword: str | None = None,
) -> str:
    f"""Compares product market price via Naver Shopping from {SERVICE}."""
    search_kw = keyword
    campaign = None
    if campaign_id:
        campaign = await fetch_campaign_by_id(campaign_id)
        if not campaign:
            raise ValueError(f"캠페인을 찾을 수 없습니다: {campaign_id}")
        search_kw = search_kw or campaign.get("title", "")

    if not search_kw:
        raise ValueError("campaign_id 또는 keyword가 필요합니다.")

    market = await search_market_price(search_kw)
    provided = None
    exp_label = "정보없음"
    if campaign:
        provided = parse_benefit_value(campaign.get("benefit") or "")
        from experience_value import experience_value_label

        exp_label = experience_value_label(provided, campaign.get("mediaType") or "블로그")

    result = {
        "keyword": search_kw,
        "min_price": market.get("min_price"),
        "max_price": market.get("max_price"),
        "avg_price": market.get("avg_price"),
        "provided_value": provided,
        "experience_value": exp_label,
    }
    if market.get("error"):
        result["notice"] = market["error"]
    return dict_to_markdown(result)


@mcp.tool(
    annotations={**READ_ONLY, "title": "Analyze Channel Profile"},
)
async def analyze_channel_profile(channel_url: str) -> str:
    f"""Analyzes reviewer channel URL from {SERVICE} for application comment generation."""
    profile = await analyze_channel(channel_url)
    if profile.get("error"):
        raise ValueError(profile["error"])
    return dict_to_markdown(profile)


@mcp.tool(
    annotations={**READ_ONLY, "title": "Generate Application Comment"},
)
async def generate_application_comment(
    campaign_id: str,
    channel_url: str | None = None,
    tone: str = "natural",
    profile: dict[str, Any] | None = None,
) -> str:
    f"""Generates a 3-sentence Korean application comment from {SERVICE}."""
    campaign = await fetch_campaign_by_id(campaign_id)
    if not campaign:
        raise ValueError(f"캠페인을 찾을 수 없습니다: {campaign_id}")

    stored = get_profile(profile_fallback=profile) or profile or {}
    url = channel_url or stored.get("channel_url")
    if not url:
        raise ValueError("channel_url이 필요합니다. 블로그 URL을 입력하거나 프로필에 저장하세요.")

    channel = await analyze_channel(url)
    if channel.get("error"):
        raise ValueError(channel["error"])

    result = generate_comment(campaign, channel, tone=tone)
    lines = [
        "## 신청 한마디",
        "",
        result["comment"],
        "",
        f"_{result['channel_evidence']}_",
        f"_{result['tips_reference']}_",
    ]
    return "\n".join(lines)


@mcp.tool(
    annotations={**READ_ONLY, "title": "Get Campaign Link"},
)
async def get_campaign_link(campaign_id: str) -> str:
    f"""Returns application page URL for a campaign from {SERVICE}."""
    if not campaign_id or not str(campaign_id).strip():
        raise ValueError("campaign_id가 필요합니다.")
    campaign = await fetch_campaign_by_id(campaign_id.strip())
    if not campaign:
        raise ValueError(f"캠페인을 찾을 수 없습니다: {campaign_id}")
    url = campaign.get("originalUrl")
    if not url:
        raise ValueError("신청 링크(originalUrl)가 없습니다.")
    return dict_to_markdown(
        {
            "campaign_id": campaign_id,
            "platform": campaign.get("platform"),
            "title": campaign.get("title"),
            "apply_url": url,
        }
    )


@mcp.tool(
    annotations={**READ_ONLY, "title": "Sponsorship Aptitude Test"},
)
def run_sponsorship_aptitude_test(answers: dict[str, Any]) -> str:
    f"""Runs one-shot sponsorship aptitude test from {SERVICE}. Returns type and filter preset."""
    result = run_aptitude_test(answers)
    return dict_to_markdown(result)


@mcp.tool(
    annotations={**READ_ONLY, "title": "Sponsorship Tips"},
)
def get_sponsorship_tips(
    topic: str = "auto",
    query: str | None = None,
    use_profile: bool = True,
    profile: dict[str, Any] | None = None,
) -> str:
    f"""Delivers verified sponsorship coaching tips from {SERVICE} static knowledge base."""
    stored = get_profile(profile_fallback=profile) if use_profile else None
    if use_profile and profile and not stored:
        stored = profile
    tip = get_sponsorship_tip(topic=topic, query=query, profile=stored, use_profile=use_profile)
    lines = [
        tip["sections_markdown"],
        "",
        "### 실행 체크리스트",
    ]
    for item in tip.get("action_checklist", []):
        lines.append(f"- [ ] {item}")
    if tip.get("next_recommended_tip"):
        lines.append(f"\n**다음 추천 팁**: `{tip['next_recommended_tip']}`")
    return "\n".join(lines)


@mcp.tool(
    annotations={**WRITE_PROFILE, "title": "Set Reviewer Profile"},
)
def set_reviewer_profile(
    channel_url: str | None = None,
    aptitude_type: str | None = None,
    preferred_media: str | None = None,
    preferred_category: str | None = None,
    preferred_type: str | None = None,
    region: str | None = None,
    experience_level: str | None = None,
    read_tip_ids: list[str] | None = None,
    profile: dict[str, Any] | None = None,
) -> str:
    f"""Saves or updates reviewer profile for {SERVICE}. Stateless — profile only, no session."""
    updates = {
        k: v
        for k, v in {
            "channel_url": channel_url,
            "aptitude_type": aptitude_type,
            "preferred_media": preferred_media,
            "preferred_category": preferred_category,
            "preferred_type": preferred_type,
            "region": region,
            "experience_level": experience_level,
            "read_tip_ids": read_tip_ids,
        }.items()
        if v is not None
    }
    saved = set_profile(updates, profile_fallback=profile)
    return dict_to_markdown({"status": "saved", "profile": saved})


@mcp.tool(
    annotations={**READ_ONLY, "title": "Get Reviewer Profile"},
)
def get_reviewer_profile(profile: dict[str, Any] | None = None) -> str:
    f"""Retrieves saved reviewer profile and filter defaults from {SERVICE}."""
    stored = get_profile(profile_fallback=profile)
    if not stored:
        return dict_to_markdown(
            {
                "has_profile": False,
                "message": "프로필이 없습니다. run_sponsorship_aptitude_test로 적성 테스트를 먼저 진행하세요.",
                "next_action": "run_sponsorship_aptitude_test",
            }
        )
    from tips_loader import auto_recommend_topic

    return dict_to_markdown(
        {
            "has_profile": True,
            "profile": stored,
            "filter_defaults": filter_defaults(stored),
            "next_recommended_tip": auto_recommend_topic(stored),
        }
    )


install_tool_error_wrapping(mcp)


def main() -> None:
    mcp.run(transport="streamable-http")


if __name__ == "__main__":
    main()
