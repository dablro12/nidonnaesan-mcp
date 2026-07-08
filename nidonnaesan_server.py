"""nidonnaesan(니돈내산) MCP Server — PlayMCP Streamable HTTP."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Annotated, Any

_APP_DIR = Path(__file__).resolve().parent / "src"
if str(_APP_DIR) not in sys.path:
    sys.path.insert(0, str(_APP_DIR))

from dotenv import load_dotenv

load_dotenv()

from mcp.server.fastmcp import FastMCP
from pydantic import Field

from application_comment import generate_comment
from aptitude_test import run_aptitude_test
from campaign_client import fetch_all_campaigns, resolve_campaign_id
from campaign_filters import hot_campaigns, search_by_need, urgent_campaigns
from campaign_formatter import compare_to_markdown, dict_to_markdown
from campaign_output import build_campaign_table
from campaign_recommender import recommend_campaigns
from campaign_resolver import resolve_campaign
from channel_profile import analyze_channel, channel_from_campaign
from experience_value import enrich_campaign, experience_value_label, parse_benefit_value
from mcp_tool_result import install_tool_error_wrapping
from naver_shopping import search_market_price
from price_enrichment import clean_search_keyword
from product_research import research_product_context
from filter_aliases import localize_filters, normalize_sort_by
from profile_store import filter_defaults, get_profile, set_profile
from tips_loader import get_sponsorship_tip
from constants import MCP_DISPLAY_NAME, MCP_ID
from tool_descriptions import mcp_description, tool_description

MCP_HOST = os.getenv("MCP_HOST", "0.0.0.0")
MCP_PORT = int(os.getenv("MCP_PORT", "8000"))
SERVICE = MCP_DISPLAY_NAME

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

TopN = Annotated[int, Field(description="반환할 캠페인 개수입니다. 카카오톡 표에서는 보통 3~5개를 권장합니다.")]
TableFormat = Annotated[
    str,
    Field(description="표 출력 형식입니다. compact는 제품명·경쟁률·제품가격·신청 링크 4컬럼, full은 상세 비교용입니다."),
]
Filters = Annotated[
    dict[str, Any] | None,
    Field(description="추천 필터입니다. region, category, media, campaign_type 등 한국어 값을 권장합니다. 자연어가 있으면 need_text가 더 안정적입니다."),
]
Profile = Annotated[
    dict[str, Any] | None,
    Field(description="저장 프로필이 없을 때 사용할 fallback 프로필입니다. channel_url, region, preferred_category 등을 담습니다."),
]
NeedText = Annotated[
    str,
    Field(description="사용자의 협찬 니즈 문장 전체입니다. 지역·업종·배송/방문·마감·경쟁률 단서를 그대로 넣습니다."),
]
OptionalNeedText = Annotated[
    str | None,
    Field(description="사용자의 협찬 니즈 문장입니다. 예: 서울 맛집 협찬, 뷰티 배송형 경쟁 낮은 것."),
]
UserRequest = Annotated[
    str | None,
    Field(description="사용자가 보낸 원문 전체입니다. need_text와 동일하게 라우팅·필터 단서를 보존할 때 사용합니다."),
]
CampaignId = Annotated[
    str,
    Field(description="표에 나온 campaign_id입니다. 예: revu-1367756, gangnam-2229176. CMPN_xxx처럼 임의 생성하지 않습니다."),
]
OptionalCampaignId = Annotated[
    str | None,
    Field(description="표에 나온 campaign_id입니다. 모르면 product_name 또는 campaign_url을 사용합니다."),
]
ProductName = Annotated[
    str | None,
    Field(description="협찬 제품명 또는 캠페인 제목입니다. campaign_id를 모를 때 제품명으로 찾거나 시장가 비교에 사용합니다."),
]
ChannelUrl = Annotated[
    str | None,
    Field(description="네이버 블로그 URL입니다. 있으면 채널 주제와 문체를 반영해 신청 문구 품질이 좋아집니다."),
]
Region = Annotated[
    str | None,
    Field(description="지역 필터입니다. 서울, 강남, 부평처럼 한국어 지역명만 넣습니다."),
]
MaxDday = Annotated[int, Field(description="마감까지 남은 최대 D-day입니다. 오늘·내일 마감은 1, 오늘 마감만은 0을 사용합니다.")]


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


@mcp.tool(
    description=mcp_description("get_campaign_recommendations"),
    annotations={**READ_ONLY, "title": "Campaign Recommendations"},
)
async def get_campaign_recommendations(
    mode: Annotated[
        str,
        Field(description="추천 모드입니다. by_need=니즈 맞춤, easy_pick=초보·경쟁 여유, urgent=마감 임박."),
    ] = "by_need",
    need_text: OptionalNeedText = None,
    user_request: UserRequest = None,
    top_n: TopN = 5,
    sort_by: Annotated[
        str,
        Field(description="정렬 기준입니다. popular, low_competition, urgent 중 하나를 권장합니다. competition은 쓰지 않습니다."),
    ] = "popular",
    table_format: TableFormat = "compact",
    filters: Filters = None,
    profile: Profile = None,
    max_dday: MaxDday = 1,
    region: Region = None,
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


@mcp.tool(
    description=mcp_description("get_today_hot_campaigns"),
    annotations={**READ_ONLY, "title": "Today's Hot Campaigns"},
)
async def get_today_hot_campaigns(
    top_n: TopN = 5,
    filters: Filters = None,
    profile: Profile = None,
    table_format: TableFormat = "compact",
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


@mcp.tool(
    description=mcp_description("search_campaigns_by_need"),
    annotations={**READ_ONLY, "title": "Search Campaigns by Need"},
)
async def search_campaigns_by_need(
    need_text: NeedText,
    top_n: TopN = 5,
    filters: Filters = None,
    profile: Profile = None,
    table_format: TableFormat = "compact",
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


@mcp.tool(
    description=mcp_description("get_urgent_campaigns"),
    annotations={**READ_ONLY, "title": "Urgent Deadline Campaigns"},
)
async def get_urgent_campaigns(
    top_n: TopN = 5,
    max_dday: MaxDday = 1,
    filters: Filters = None,
    profile: Profile = None,
    region: Region = None,
    table_format: TableFormat = "compact",
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


@mcp.tool(
    description=mcp_description("compare_product_market_price"),
    annotations={**READ_ONLY, "title": "Compare Market Price"},
)
async def compare_product_market_price(
    campaign_id: OptionalCampaignId = None,
    keyword: Annotated[
        str | None,
        Field(description="네이버 쇼핑에서 검색할 제품 키워드입니다. campaign_id가 불명확하면 제품명 키워드를 우선 사용합니다."),
    ] = None,
    product_name: ProductName = None,
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


@mcp.tool(
    description=mcp_description("analyze_channel_profile"),
    annotations={**READ_ONLY, "title": "Analyze Channel Profile"},
)
async def analyze_channel_profile(
    channel_url: Annotated[str, Field(description="분석할 네이버 블로그 URL입니다. 예: https://blog.naver.com/아이디")],
) -> str:
    profile = await analyze_channel(channel_url)
    if profile.get("error"):
        raise ValueError(profile["error"])
    return dict_to_markdown(profile)


analyze_channel_profile.__doc__ = f"Analyzes Naver blog channel from {SERVICE}."


@mcp.tool(
    description=mcp_description("generate_application_comment"),
    annotations={**READ_ONLY, "title": "Generate Application Comment"},
)
async def generate_application_comment(
    campaign_id: OptionalCampaignId = None,
    product_name: ProductName = None,
    campaign_url: Annotated[
        str | None,
        Field(description="원본 협찬 신청 URL입니다. campaign_id와 product_name을 모를 때 캠페인 식별에 사용합니다."),
    ] = None,
    channel_url: ChannelUrl = None,
    tone: Annotated[
        str,
        Field(description="신청 문구 톤입니다. natural, polite, appeal 중 하나를 권장합니다."),
    ] = "natural",
    profile: Profile = None,
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
    url = (channel_url or stored.get("channel_url") or "").strip()
    channel_source = "channel"

    if url:
        channel = await analyze_channel(url)
        if channel.get("error"):
            raise ValueError(channel["error"])
    else:
        channel = channel_from_campaign(campaign)
        channel_source = "campaign"

    title = campaign.get("title") or product_name or ""
    research = await research_product_context(clean_search_keyword(title))
    product_ctx = research.get("context")

    result = generate_comment(campaign, channel, tone=tone, product_context=product_ctx)
    lines = [
        "## 신청 한마디",
        "",
    ]
    if channel_source == "campaign":
        lines.append("_블로그 URL 없음 — 캠페인·제품 정보 기반 초안입니다. 본인 채널에 맞게 수정하세요._")
        lines.append("")
    lines.extend(
        [
            result["comment"],
            "",
            f"_{result['channel_evidence']}_",
            f"_{result['tips_reference']}_",
            "",
            result.get("verification_footer", ""),
            f"_매칭: {match_mode} · campaign_id: {campaign.get('id')}_",
        ]
    )
    return "\n".join(lines)


generate_application_comment.__doc__ = tool_description(
    f"3-sentence application draft from {SERVICE}.",
    "generate_application_comment",
)


@mcp.tool(
    description=mcp_description("get_campaign_link"),
    annotations={**READ_ONLY, "title": "Get Campaign Link"},
)
async def get_campaign_link(campaign_id: CampaignId) -> str:
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


@mcp.tool(
    description=mcp_description("run_sponsorship_aptitude_test"),
    annotations={**READ_ONLY, "title": "Sponsorship Aptitude Test"},
)
def run_sponsorship_aptitude_test(
    answers: Annotated[
        dict[str, Any],
        Field(description="적성 테스트 답변 객체입니다. 매체, 관심 업종, 지역, 가능 빈도, 선호 체험 방식 등을 담습니다."),
    ],
) -> str:
    result = run_aptitude_test(answers)
    return dict_to_markdown(result)


run_sponsorship_aptitude_test.__doc__ = tool_description(
    f"One-shot aptitude test from {SERVICE}. USE FIRST for 협찬 처음.",
    "run_sponsorship_aptitude_test",
)


@mcp.tool(
    description=mcp_description("get_sponsorship_tips"),
    annotations={**READ_ONLY, "title": "Sponsorship Tips"},
)
def get_sponsorship_tips(
    topic: Annotated[
        str,
        Field(description="팁 주제입니다. auto, selection_rate, platform, ad_disclosure, blog_index, posting_omission 등을 권장합니다."),
    ] = "auto",
    query: Annotated[
        str | None,
        Field(description="사용자가 궁금해한 팁 질문 원문입니다. 예: 선정률 올리는 법, 광고 표기 방법."),
    ] = None,
    use_profile: Annotated[bool, Field(description="저장된 리뷰어 프로필을 반영해 팁을 맞춤 추천할지 여부입니다.")] = True,
    profile: Profile = None,
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


@mcp.tool(
    description=mcp_description("set_reviewer_profile"),
    annotations={**WRITE_PROFILE, "title": "Set Reviewer Profile"},
)
def set_reviewer_profile(
    channel_url: ChannelUrl = None,
    aptitude_type: Annotated[
        str | None,
        Field(description="적성 테스트 결과 유형입니다. 예: food_explorer, beauty_creator, lifestyle_recorder."),
    ] = None,
    preferred_media: Annotated[
        str | None,
        Field(description="선호 리뷰 매체입니다. 예: 블로그, 인스타릴스, 인스타그램."),
    ] = None,
    preferred_category: Annotated[
        str | None,
        Field(description="선호 협찬 업종입니다. 예: 맛집, 뷰티, 숙박, 생활, 디지털가전."),
    ] = None,
    preferred_type: Annotated[
        str | None,
        Field(description="선호 체험 방식입니다. 방문형 또는 배송형을 권장합니다."),
    ] = None,
    region: Region = None,
    experience_level: Annotated[
        str | None,
        Field(description="협찬 경험 수준입니다. beginner, intermediate, advanced 또는 한국어 표현을 사용할 수 있습니다."),
    ] = None,
    read_tip_ids: Annotated[
        list[str] | None,
        Field(description="이미 읽은 팁 ID 목록입니다. 중복 추천을 줄이는 데 사용합니다."),
    ] = None,
    profile: Profile = None,
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


@mcp.tool(
    description=mcp_description("get_reviewer_profile"),
    annotations={**READ_ONLY, "title": "Get Reviewer Profile"},
)
def get_reviewer_profile(profile: Profile = None) -> str:
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
