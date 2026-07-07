"""nidonnaesan(니돈내산) MCP Server — PlayMCP Streamable HTTP."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

_APP_DIR = Path(__file__).resolve().parent / "src"
if str(_APP_DIR) not in sys.path:
    sys.path.insert(0, str(_APP_DIR))

from dotenv import load_dotenv

load_dotenv()

from mcp.server.fastmcp import FastMCP

from application_comment import generate_comment
from aptitude_test import run_aptitude_test
from campaign_client import fetch_all_campaigns, resolve_campaign_id
from campaign_filters import hot_campaigns, search_by_need, urgent_campaigns
from campaign_formatter import compare_to_markdown, dict_to_markdown
from campaign_output import build_campaign_table
from campaign_recommender import recommend_campaigns
from campaign_resolver import resolve_campaign
from channel_profile import analyze_channel
from experience_value import enrich_campaign, experience_value_label, parse_benefit_value
from mcp_tool_result import install_tool_error_wrapping
from naver_shopping import search_market_price
from price_enrichment import clean_search_keyword
from product_research import research_product_context
from filter_aliases import localize_filters, normalize_sort_by
from profile_store import filter_defaults, get_profile, set_profile
from tips_loader import get_sponsorship_tip
from tool_descriptions import tool_description

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
    raw = filters if filters else filter_defaults(profile or {})
    return localize_filters(raw) if raw else {}


def _format_recommendation_header(meta: dict[str, Any], need_text: str | None = None) -> str:
    mode = meta.get("mode", "by_need")
    if mode == "easy_pick":
        return "초보 추천 — 경쟁 여유·체험가치 중심"
    if mode == "urgent":
        region = meta.get("region")
        dday = meta.get("max_dday", 1)
        title = f"마감 임박 협찬 (D-{dday} 이내)"
        return f"{title} — {region}" if region else title
    if need_text:
        header = f"니즈 맞춤: {need_text}"
        intent = meta.get("intent") or {}
        if intent.get("regions"):
            header += f" (지역: {', '.join(intent['regions'][:3])})"
        if intent.get("categories"):
            header += f" (업종: {', '.join(intent['categories'])})"
        if meta.get("sort_by") == "low_competition":
            header += " — 경쟁률 낮은 순"
        return header
    return "맞춤 협찬 추천"


@mcp.tool(annotations={**READ_ONLY, "title": "Campaign Recommendations"})
async def get_campaign_recommendations(
    mode: str = "by_need",
    need_text: str | None = None,
    user_request: str | None = None,
    top_n: int = 5,
    sort_by: str = "popular",
    table_format: str = "compact",
    filters: dict[str, Any] | None = None,
    profile: dict[str, Any] | None = None,
    max_dday: int = 1,
    region: str | None = None,
) -> str:
    stored = get_profile(profile_fallback=profile) or profile
    effective_filters = _resolve_filters(filters, stored)
    if region:
        effective_filters = {**effective_filters, "region": localize_filters({"region": region}).get("region", region)}

    effective_need = (need_text or user_request or "").strip() or None
    effective_sort = normalize_sort_by(sort_by)

    if effective_sort == "low_competition" and not effective_need:
        mode = "easy_pick"

    campaigns = await fetch_all_campaigns()
    picked, meta = recommend_campaigns(
        campaigns,
        mode=mode,
        need_text=effective_need,
        top_n=top_n,
        filters=effective_filters,
        sort_by=effective_sort,
        max_dday=max_dday,
        region=effective_filters.get("region"),
    )
    title = _format_recommendation_header(meta, effective_need or meta.get("synthetic_need_text"))
    return await build_campaign_table(picked, title=title, table_format=table_format)


get_campaign_recommendations.__doc__ = tool_description(
    f"Unified sponsorship recommendations from {SERVICE}. Default: compact Markdown table with prices.",
    "get_campaign_recommendations",
)


@mcp.tool(annotations={**READ_ONLY, "title": "Today's Hot Campaigns"})
async def get_today_hot_campaigns(
    top_n: int = 5,
    filters: dict[str, Any] | None = None,
    profile: dict[str, Any] | None = None,
    table_format: str = "compact",
) -> str:
    stored = get_profile(profile_fallback=profile) or profile
    effective_filters = _resolve_filters(filters, stored)
    campaigns = await fetch_all_campaigns()
    hot = hot_campaigns(campaigns, top_n=top_n, filters=effective_filters, diversify=True)
    return await build_campaign_table(
        hot, title=f"오늘의 인기 협찬 TOP {top_n}", table_format=table_format
    )


get_today_hot_campaigns.__doc__ = tool_description(
    f"Today's popular sponsorship campaigns from {SERVICE}. Diversified platforms, Markdown table.",
    "get_today_hot_campaigns",
)


@mcp.tool(annotations={**READ_ONLY, "title": "Search Campaigns by Need"})
async def search_campaigns_by_need(
    need_text: str,
    top_n: int = 5,
    filters: dict[str, Any] | None = None,
    profile: dict[str, Any] | None = None,
    table_format: str = "compact",
) -> str:
    stored = get_profile(profile_fallback=profile) or profile
    effective_filters = _resolve_filters(filters, stored)
    campaigns = await fetch_all_campaigns()
    matched, keywords, mode, intent = search_by_need(
        campaigns, need_text, top_n=top_n, filters=effective_filters
    )
    header = f"니즈 탐색: {need_text}"
    if intent.get("regions"):
        header += f" (지역: {', '.join(intent['regions'][:3])})"
    if intent.get("categories"):
        header += f" (업종: {', '.join(intent['categories'])})"
    if keywords:
        header += f" (키워드: {', '.join(keywords)})"
    if mode == "popular_fallback":
        header += " — 키워드 매칭 없음, 인기순으로 표시"
    return await build_campaign_table(matched, title=header, table_format=table_format)


search_campaigns_by_need.__doc__ = tool_description(
    f"Natural-language sponsorship search from {SERVICE}. Pass user sentence as need_text.",
    "search_campaigns_by_need",
)


@mcp.tool(annotations={**READ_ONLY, "title": "Urgent Deadline Campaigns"})
async def get_urgent_campaigns(
    top_n: int = 5,
    max_dday: int = 1,
    filters: dict[str, Any] | None = None,
    profile: dict[str, Any] | None = None,
    region: str | None = None,
    table_format: str = "compact",
) -> str:
    stored = get_profile(profile_fallback=profile) or profile
    effective_filters = _resolve_filters(filters, stored)
    if region:
        effective_filters = {**effective_filters, "region": region}
    elif stored and stored.get("region") and not effective_filters.get("region"):
        effective_filters = {**effective_filters, "region": stored["region"]}
    campaigns = await fetch_all_campaigns()
    urgent = urgent_campaigns(
        campaigns,
        top_n=top_n,
        max_dday=max_dday,
        filters=effective_filters,
        region=region or effective_filters.get("region"),
    )
    title = f"마감 임박 협찬 (D-{max_dday} 이내)"
    if effective_filters.get("region"):
        title += f" — {effective_filters['region']}"
    return await build_campaign_table(urgent, title=title, table_format=table_format)


get_urgent_campaigns.__doc__ = tool_description(
    f"Imminent deadline campaigns (D-0/D-1) from {SERVICE}. Markdown table.",
    "get_urgent_campaigns",
)


@mcp.tool(annotations={**READ_ONLY, "title": "Compare Market Price"})
async def compare_product_market_price(
    campaign_id: str | None = None,
    keyword: str | None = None,
    product_name: str | None = None,
) -> str:
    search_kw = keyword or product_name
    campaign = None

    if campaign_id and str(campaign_id).strip():
        campaign = await resolve_campaign_id(str(campaign_id).strip())
        if campaign:
            search_kw = search_kw or clean_search_keyword(campaign.get("title") or "")
        elif not search_kw:
            search_kw = clean_search_keyword(str(campaign_id))

    if not search_kw:
        raise ValueError(
            "keyword, product_name, 또는 표에 있는 campaign_id(revu-숫자)가 필요합니다."
        )

    market = await search_market_price(search_kw)
    provided = None
    exp_label = "정보없음"
    benefit = None
    if campaign:
        benefit = campaign.get("benefit") or ""
        provided = parse_benefit_value(benefit)
        exp_label = experience_value_label(provided, campaign.get("mediaType") or "블로그")

    result: dict[str, Any] = {
        "keyword": search_kw,
        "min_price": market.get("min_price"),
        "max_price": market.get("max_price"),
        "avg_price": market.get("avg_price"),
        "provided_value": provided,
        "benefit": benefit,
        "experience_value": exp_label,
    }
    if campaign:
        result["campaign_id"] = campaign.get("id")
        result["platform"] = campaign.get("platform")
        result["title"] = campaign.get("title")
    if market.get("error"):
        result["notice"] = market["error"]
    return compare_to_markdown(result)


compare_product_market_price.__doc__ = tool_description(
    f"Naver Shopping price compare from {SERVICE}. Prefer keyword/product_name; id format revu-NNNN.",
    "compare_product_market_price",
)


@mcp.tool(annotations={**READ_ONLY, "title": "Analyze Channel Profile"})
async def analyze_channel_profile(channel_url: str) -> str:
    profile = await analyze_channel(channel_url)
    if profile.get("error"):
        raise ValueError(profile["error"])
    return dict_to_markdown(profile)


analyze_channel_profile.__doc__ = f"Analyzes Naver blog channel from {SERVICE}."


@mcp.tool(annotations={**READ_ONLY, "title": "Generate Application Comment"})
async def generate_application_comment(
    campaign_id: str | None = None,
    product_name: str | None = None,
    campaign_url: str | None = None,
    channel_url: str | None = None,
    tone: str = "natural",
    profile: dict[str, Any] | None = None,
) -> str:
    campaign, match_mode = await resolve_campaign(
        campaign_id=campaign_id,
        product_name=product_name,
        campaign_url=campaign_url,
    )
    if not campaign:
        raise ValueError(
            "캠페인을 찾을 수 없습니다. campaign_id(revu-숫자), product_name, campaign_url 중 하나를 입력하세요."
        )

    stored = get_profile(profile_fallback=profile) or profile or {}
    url = channel_url or stored.get("channel_url")
    if not url:
        raise ValueError("channel_url이 필요합니다. 블로그 URL을 입력하거나 프로필에 저장하세요.")

    channel = await analyze_channel(url)
    if channel.get("error"):
        raise ValueError(channel["error"])

    title = campaign.get("title") or product_name or ""
    research = await research_product_context(clean_search_keyword(title))
    product_ctx = research.get("context")

    result = generate_comment(campaign, channel, tone=tone, product_context=product_ctx)
    lines = [
        "## 신청 한마디",
        "",
        result["comment"],
        "",
        f"_{result['channel_evidence']}_",
        f"_{result['tips_reference']}_",
        "",
        result.get("verification_footer", ""),
        f"_매칭: {match_mode} · campaign_id: {campaign.get('id')}_",
    ]
    return "\n".join(lines)


generate_application_comment.__doc__ = f"3-sentence application draft from {SERVICE}."


@mcp.tool(annotations={**READ_ONLY, "title": "Get Campaign Link"})
async def get_campaign_link(campaign_id: str) -> str:
    if not campaign_id or not str(campaign_id).strip():
        raise ValueError("campaign_id가 필요합니다 (예: revu-1367756).")
    campaign = await resolve_campaign_id(campaign_id.strip())
    if not campaign:
        raise ValueError(
            f"캠페인을 찾을 수 없습니다: {campaign_id}. 표의 id(revu-숫자)를 사용하세요."
        )
    url = campaign.get("originalUrl")
    if not url:
        raise ValueError("신청 링크(originalUrl)가 없습니다.")
    return dict_to_markdown(
        {
            "campaign_id": campaign.get("id"),
            "platform": campaign.get("platform"),
            "title": campaign.get("title"),
            "apply_url": url,
        }
    )


get_campaign_link.__doc__ = f"Application URL from {SERVICE}. Use id like revu-1367756."


@mcp.tool(annotations={**READ_ONLY, "title": "Sponsorship Aptitude Test"})
def run_sponsorship_aptitude_test(answers: dict[str, Any]) -> str:
    result = run_aptitude_test(answers)
    return dict_to_markdown(result)


run_sponsorship_aptitude_test.__doc__ = tool_description(
    f"One-shot aptitude test from {SERVICE}. USE FIRST for 협찬 처음.",
    "run_sponsorship_aptitude_test",
)


@mcp.tool(annotations={**READ_ONLY, "title": "Sponsorship Tips"})
def get_sponsorship_tips(
    topic: str = "auto",
    query: str | None = None,
    use_profile: bool = True,
    profile: dict[str, Any] | None = None,
) -> str:
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
        lines.append(
            "\n_협찬 처음이면 다음: `get_campaign_recommendations(mode=easy_pick)` 호출_"
        )
    return "\n".join(lines)


get_sponsorship_tips.__doc__ = tool_description(
    f"Sponsorship coaching tips from {SERVICE}.",
    "get_sponsorship_tips",
)


@mcp.tool(annotations={**WRITE_PROFILE, "title": "Set Reviewer Profile"})
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


set_reviewer_profile.__doc__ = f"Save reviewer profile for {SERVICE}."


@mcp.tool(annotations={**READ_ONLY, "title": "Get Reviewer Profile"})
def get_reviewer_profile(profile: dict[str, Any] | None = None) -> str:
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


get_reviewer_profile.__doc__ = f"Get reviewer profile from {SERVICE}."


install_tool_error_wrapping(mcp)


def main() -> None:
    from campaign_sync import start_background_sync

    start_background_sync()
    mcp.run(transport="streamable-http")


if __name__ == "__main__":
    main()
