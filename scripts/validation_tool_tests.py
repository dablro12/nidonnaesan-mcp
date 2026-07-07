#!/usr/bin/env python3
"""MCP 툴별 검증 시나리오 10개씩 실행 (간단→복잡)."""

from __future__ import annotations

import asyncio
import json
import sys
import traceback
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
load_dotenv(ROOT / ".env")

from application_comment import generate_comment
from aptitude_test import run_aptitude_test
from campaign_client import fetch_all_campaigns, fetch_campaign_by_id
from campaign_filters import hot_campaigns, search_by_need
from campaign_formatter import campaigns_to_markdown, dict_to_markdown
from channel_profile import analyze_channel
from experience_value import enrich_campaign
from naver_shopping import search_market_price
from profile_store import filter_defaults, get_profile, set_profile
from tips_loader import get_sponsorship_tip

SAMPLE_BLOG = "https://blog.naver.com/dablro12"
DB_KEY = {"_user_key": "validation:test"}


@dataclass
class Case:
    level: str  # simple | medium | complex
    name: str
    fn: Callable
    kwargs: dict[str, Any]
    expect_error: bool = False


def _preview(result: Any, max_len: int = 400) -> str:
    if isinstance(result, str):
        text = result
    else:
        text = json.dumps(result, ensure_ascii=False, indent=2)
    text = text.replace("\n", " ")
    return text[:max_len] + ("..." if len(text) > max_len else "")


async def run_case(case: Case) -> dict[str, Any]:
    try:
        fn = case.fn
        if asyncio.iscoroutinefunction(fn):
            result = await fn(**case.kwargs)
        else:
            result = fn(**case.kwargs)
        status = "OK"
        err = None
    except Exception as exc:
        if case.expect_error:
            status = "OK"
            err = f"(expected) {exc.__class__.__name__}: {exc}"
            result = None
        else:
            status = "FAIL"
            result = None
            err = f"{exc.__class__.__name__}: {exc}"
    return {
        "level": case.level,
        "name": case.name,
        "status": status,
        "preview": _preview(result) if result is not None else None,
        "error": err,
    }


# --- Tool runners ---

async def hot(top_n=5, filters=None, profile=None):
    campaigns = await fetch_all_campaigns()
    stored = get_profile(profile_fallback=profile) or profile
    f = filters or filter_defaults(stored or {})
    hot_list = hot_campaigns(campaigns, top_n=top_n, filters=f or None)
    rows = [enrich_campaign(c) for c in hot_list]
    return {"count": len(rows), "markdown_head": campaigns_to_markdown(rows)[:500]}


async def search(need_text, top_n=5, filters=None, profile=None):
    campaigns = await fetch_all_campaigns()
    stored = get_profile(profile_fallback=profile) or profile
    f = filters or filter_defaults(stored or {})
    matched, kws, mode, _intent = search_by_need(campaigns, need_text, top_n=top_n, filters=f or None)
    rows = [enrich_campaign(c) for c in matched]
    return {"keywords": kws, "mode": mode, "count": len(rows), "titles": [r["title"] for r in rows[:3]]}


async def market_price(campaign_id=None, keyword=None):
    kw = keyword
    campaign = None
    if campaign_id:
        campaign = await fetch_campaign_by_id(campaign_id)
        if not campaign and not kw:
            raise ValueError(f"캠페인을 찾을 수 없습니다: {campaign_id}")
        kw = kw or (campaign or {}).get("title", "")
    if not kw:
        raise ValueError("campaign_id 또는 keyword가 필요합니다.")
    market = await search_market_price(kw)
    return {"keyword": kw, "market": market, "campaign_found": campaign is not None}


async def channel(url):
    return await analyze_channel(url)


async def app_comment(campaign_id, channel_url=None, tone="natural", profile=None):
    campaign = await fetch_campaign_by_id(campaign_id)
    if not campaign:
        raise ValueError("campaign not found")
    stored = get_profile(profile_fallback=profile) or profile or {}
    url = channel_url or stored.get("channel_url") or SAMPLE_BLOG
    ch = await analyze_channel(url)
    if ch.get("error"):
        raise ValueError(ch["error"])
    return generate_comment(campaign, ch, tone=tone)


async def link(campaign_id):
    if not campaign_id or not str(campaign_id).strip():
        raise ValueError("campaign_id가 필요합니다.")
    c = await fetch_campaign_by_id(campaign_id.strip())
    if not c:
        raise ValueError(f"캠페인을 찾을 수 없습니다: {campaign_id}")
    return {"apply_url": c.get("originalUrl"), "platform": c.get("platform")}


def aptitude(answers):
    return run_aptitude_test(answers)


def tips(topic="auto", query=None, use_profile=True, profile=None):
    stored = get_profile(profile_fallback=profile) if use_profile else None
    if use_profile and profile and not stored:
        stored = profile
    tip = get_sponsorship_tip(topic=topic, query=query, profile=stored, use_profile=use_profile)
    return {"tip_id": tip["tip_id"], "title": tip["title"], "next": tip.get("next_recommended_tip")}


def set_prof(**kwargs):
    profile = kwargs.pop("profile", None)
    updates = {k: v for k, v in kwargs.items() if v is not None}
    saved = set_profile(updates, profile_fallback=profile or DB_KEY)
    return {"status": "saved", "keys": list(saved.keys())}


def get_prof(profile=None):
    stored = get_profile(profile_fallback=profile or DB_KEY)
    if not stored:
        return {"has_profile": False}
    return {"has_profile": True, "aptitude": stored.get("aptitude_type"), "filters": filter_defaults(stored)}


async def get_sample_campaign_id() -> str | None:
    camps = await fetch_all_campaigns()
    return camps[0]["id"] if camps else None


async def build_cases() -> dict[str, list[Case]]:
    cid = await get_sample_campaign_id() or "revu-1367721"

    return {
        "get_today_hot_campaigns": [
            Case("simple", "기본 5개", hot, {}),
            Case("simple", "top_n=3", hot, {"top_n": 3}),
            Case("medium", "맛집 필터", hot, {"filters": {"category": "맛집"}, "top_n": 5}),
            Case("medium", "배송형+블로그", hot, {"filters": {"type": "배송형", "mediaType": "블로그"}, "top_n": 5}),
            Case("medium", "플랫폼 레뷰", hot, {"filters": {"platform": "레뷰"}, "top_n": 5}),
            Case("complex", "프로필 필터 적용", hot, {"profile": {"preferred_category": "뷰티", "preferred_type": "배송형"}, "top_n": 5}),
            Case("complex", "top_n=10 전체", hot, {"top_n": 10}),
            Case("complex", "숙박 카테고리", hot, {"filters": {"category": "숙박"}, "top_n": 5}),
            Case("complex", "인스타릴스 매체", hot, {"filters": {"mediaType": "인스타릴스"}, "top_n": 5}),
            Case("complex", "기자단 타입", hot, {"filters": {"type": "기자단"}, "top_n": 5}),
        ],
        "search_campaigns_by_need": [
            Case("simple", "튜브 키워드", search, {"need_text": "튜브"}),
            Case("simple", "맛집", search, {"need_text": "맛집 협찬"}),
            Case("medium", "아이 튜브", search, {"need_text": "아이가 놀 수 있는 튜브 협찬"}),
            Case("medium", "뷰티 릴스", search, {"need_text": "뷰티 인스타 릴스", "filters": {"mediaType": "인스타릴스"}}),
            Case("medium", "강남 카페", search, {"need_text": "강남 카페 방문형"}),
            Case("complex", "긴 자연어+필터", search, {"need_text": "육아용품 생활 배송 협찬 찾아줘", "filters": {"type": "배송형"}, "top_n": 5}),
            Case("complex", "반려동물 키워드", search, {"need_text": "강아지 간식 반려동물", "filters": {"category": "반려동물"}}),
            Case("complex", "디지털 가전", search, {"need_text": "이어폰 디지털 가전", "filters": {"category": "디지털"}}),
            Case("complex", "숙박 여행", search, {"need_text": "제주 숙박 펜션 여행"}),
            Case("complex", "프로필+니즈", search, {"need_text": "방문 체험", "profile": {"preferred_category": "맛집", "preferred_type": "방문형"}}),
        ],
        "compare_product_market_price": [
            Case("simple", "키워드만: 이어폰", market_price, {"keyword": "무선 이어폰"}),
            Case("simple", "키워드: 립스틱", market_price, {"keyword": "립스틱"}),
            Case("medium", "캠페인ID", market_price, {"campaign_id": cid}),
            Case("medium", "키워드: 튜브", market_price, {"keyword": "아이 물놀이 튜브"}),
            Case("medium", "키워드: 향수", market_price, {"keyword": "향수"}),
            Case("complex", "캠페인+키워드 오버라이드", market_price, {"campaign_id": cid, "keyword": "맛집"}),
            Case("complex", "긴 키워드", market_price, {"keyword": "강아지 사료 5kg"}),
            Case("complex", "영문 키워드", market_price, {"keyword": "bluetooth speaker"}),
            Case("complex", "존재하지 않는 ID", market_price, {"campaign_id": "invalid-id-999"}, expect_error=True),
            Case("complex", "빈 키워드 없음", market_price, {}, expect_error=True),
        ],
        "analyze_channel_profile": [
            Case("simple", "기본 블로그", channel, {"url": SAMPLE_BLOG}),
            Case("medium", "m.blog URL", channel, {"url": "https://m.blog.naver.com/dablro12"}),
            Case("complex", "잘못된 URL", channel, {"url": "https://example.com/not-blog"}),
            Case("complex", "빈 도메인", channel, {"url": "https://blog.naver.com/"}),
            Case("simple", "다른 블로그ID", channel, {"url": "https://blog.naver.com/naver"}),
            Case("medium", "https 없음 형식", channel, {"url": "blog.naver.com/dablro12"}),
            Case("medium", "경로 포함", channel, {"url": f"{SAMPLE_BLOG}/223562345678"}),
            Case("complex", "인스타 URL", channel, {"url": "https://instagram.com/test"}),
            Case("complex", "유튜브 URL", channel, {"url": "https://youtube.com/@test"}),
            Case("complex", "깨진 URL", channel, {"url": "not-a-url"}),
        ],
        "generate_application_comment": [
            Case("simple", "기본 톤", app_comment, {"campaign_id": cid}),
            Case("medium", "polite 톤", app_comment, {"campaign_id": cid, "tone": "polite"}),
            Case("medium", "appeal 톤", app_comment, {"campaign_id": cid, "tone": "appeal"}),
            Case("complex", "채널 URL 지정", app_comment, {"campaign_id": cid, "channel_url": SAMPLE_BLOG}),
            Case("complex", "프로필 channel_url", app_comment, {"campaign_id": cid, "profile": {"channel_url": SAMPLE_BLOG}}),
            Case("complex", "잘못된 캠페인ID", app_comment, {"campaign_id": "no-such-id"}, expect_error=True),
            Case("complex", "채널 없음", app_comment, {"campaign_id": cid, "channel_url": None, "profile": {}}, expect_error=True),
            Case("medium", "맛집 니즈 캠페인", app_comment, {"campaign_id": cid, "tone": "natural"}),
            Case("simple", "natural 재확인", app_comment, {"campaign_id": cid, "tone": "natural"}),
            Case("complex", "invalid blog", app_comment, {"campaign_id": cid, "channel_url": "https://blog.naver.com/__nonexistent_xyz__"}, expect_error=True),
        ],
        "get_campaign_link": [
            Case("simple", "유효 ID", link, {"campaign_id": cid}),
            Case("complex", "invalid ID", link, {"campaign_id": "fake-000"}, expect_error=True),
            Case("simple", "하드코딩 revu", link, {"campaign_id": "revu-1367721"}),
            Case("medium", "다른 플랫폼 ID", link, {"campaign_id": cid}),
            Case("medium", "빈 문자열", link, {"campaign_id": ""}, expect_error=True),
            Case("complex", "특수문자 ID", link, {"campaign_id": "revu-<script>"}, expect_error=True),
            Case("simple", "재조회", link, {"campaign_id": cid}),
            Case("medium", "긴 ID", link, {"campaign_id": "revu-" + "1" * 20}, expect_error=True),
            Case("complex", "null형", link, {"campaign_id": "null"}, expect_error=True),
            Case("complex", "숫자만", link, {"campaign_id": "1367721"}, expect_error=True),
        ],
        "run_sponsorship_aptitude_test": [
            Case("simple", "맛집 블로거", aptitude, {"answers": {"channel_type": "blog", "interest_category": "맛집", "region": "서울", "posting_frequency": "yes", "campaign_type_pref": "방문형", "sponsorship_experience": "no"}}),
            Case("simple", "뷰티 인스타", aptitude, {"answers": {"channel_type": "instagram", "interest_category": "뷰티", "region": "수도권", "posting_frequency": "yes", "campaign_type_pref": "배송형", "content_format": "video", "sponsorship_experience": "no"}}),
            Case("medium", "여행러", aptitude, {"answers": {"channel_type": "blog", "interest_category": "여행", "region": "전국", "posting_frequency": "yes", "campaign_type_pref": "방문형", "sponsorship_experience": "yes"}}),
            Case("medium", "생활 기록자", aptitude, {"answers": {"channel_type": "blog", "interest_category": "생활", "region": "지방", "posting_frequency": "no", "campaign_type_pref": "배송형", "sponsorship_experience": "no"}}),
            Case("complex", "완전 초보", aptitude, {"answers": {"channel_type": "none", "interest_category": "맛집", "region": "서울", "posting_frequency": "no", "campaign_type_pref": "상관없음", "sponsorship_experience": "no"}}),
            Case("complex", "디지털", aptitude, {"answers": {"channel_type": "youtube", "interest_category": "디지털", "region": "수도권", "posting_frequency": "yes", "campaign_type_pref": "배송형", "content_format": "video", "sponsorship_experience": "yes"}}),
            Case("complex", "반려", aptitude, {"answers": {"channel_type": "blog", "interest_category": "반려", "region": "서울", "posting_frequency": "yes", "campaign_type_pref": "배송형", "sponsorship_experience": "no"}}),
            Case("medium", "유튜브 올라운더", aptitude, {"answers": {"channel_type": "youtube", "interest_category": "생활", "region": "전국", "posting_frequency": "yes", "campaign_type_pref": "상관없음", "sponsorship_experience": "yes"}}),
            Case("simple", "인스타 뷰티 경험자", aptitude, {"answers": {"channel_type": "instagram", "interest_category": "뷰티", "region": "서울", "posting_frequency": "yes", "campaign_type_pref": "배송형", "sponsorship_experience": "yes"}}),
            Case("complex", "모든 필드", aptitude, {"answers": {"channel_type": "blog", "interest_category": "맛집", "region": "서울", "posting_frequency": "yes", "campaign_type_pref": "방문형", "content_format": "both", "sponsorship_experience": "no"}}),
        ],
        "get_sponsorship_tips": [
            Case("simple", "topic=selection_rate", tips, {"topic": "selection_rate", "use_profile": False}),
            Case("simple", "topic=platform", tips, {"topic": "platform", "use_profile": False}),
            Case("medium", "query 광고표기", tips, {"query": "광고 표기 어떻게", "use_profile": False}),
            Case("medium", "query 누락", tips, {"query": "포스팅 누락", "use_profile": False}),
            Case("medium", "topic=blog_index", tips, {"topic": "blog_index", "use_profile": False}),
            Case("complex", "auto 초보", tips, {"topic": "auto", "profile": {"experience_level": "none", "read_tip_ids": []}}),
            Case("complex", "auto 중급+읽음", tips, {"topic": "auto", "profile": {"experience_level": "intermediate", "read_tip_ids": ["selection_rate", "platform"]}}),
            Case("complex", "auto 채널있음", tips, {"topic": "auto", "profile": {"experience_level": "beginner", "channel_url": SAMPLE_BLOG, "read_tip_ids": []}}),
            Case("complex", "query 선정률", tips, {"query": "선정률 올리는 법", "use_profile": False}),
            Case("complex", "topic=ad_disclosure", tips, {"topic": "ad_disclosure", "use_profile": False}),
        ],
        "set_reviewer_profile": [
            Case("simple", "적성만", set_prof, {"aptitude_type": "food_explorer", "profile": DB_KEY}),
            Case("medium", "채널+카테고리", set_prof, {"channel_url": SAMPLE_BLOG, "preferred_category": "맛집", "profile": DB_KEY}),
            Case("medium", "read_tip_ids", set_prof, {"read_tip_ids": ["selection_rate"], "profile": DB_KEY}),
            Case("complex", "전체 필드", set_prof, {"channel_url": SAMPLE_BLOG, "aptitude_type": "beauty_creator", "preferred_media": "인스타릴스", "preferred_category": "뷰티", "preferred_type": "배송형", "region": "서울", "experience_level": "beginner", "profile": DB_KEY}),
            Case("complex", "tip 누적", set_prof, {"read_tip_ids": ["platform"], "profile": DB_KEY}),
            Case("simple", "region만", set_prof, {"region": "수도권", "profile": DB_KEY}),
            Case("medium", "experience intermediate", set_prof, {"experience_level": "intermediate", "profile": DB_KEY}),
            Case("complex", "traveler 유형", set_prof, {"aptitude_type": "traveler", "preferred_category": "숙박", "profile": DB_KEY}),
            Case("medium", "media 유튜브", set_prof, {"preferred_media": "유튜브", "profile": DB_KEY}),
            Case("simple", "all_rounder", set_prof, {"aptitude_type": "all_rounder", "profile": DB_KEY}),
        ],
        "get_reviewer_profile": [
            Case("simple", "저장 후 조회", get_prof, {"profile": DB_KEY}),
            Case("medium", "filter_defaults 확인", get_prof, {"profile": DB_KEY}),
            Case("complex", "빈 프로필 키", get_prof, {"profile": {"_user_key": "validation:empty"}}),
            Case("simple", "재조회", get_prof, {"profile": DB_KEY}),
            Case("medium", "anonymous", get_prof, {"profile": {"_user_key": "validation:empty"}}),
            Case("complex", "다른 키", get_prof, {"profile": {"_user_key": "validation:other"}}),
            Case("simple", "기본키", get_prof, {"profile": DB_KEY}),
            Case("medium", "tip 이력 확인", get_prof, {"profile": DB_KEY}),
            Case("complex", "aptitude 확인", get_prof, {"profile": DB_KEY}),
            Case("simple", "최종 조회", get_prof, {"profile": DB_KEY}),
        ],
    }


async def main() -> None:
    all_cases = await build_cases()
    summary: dict[str, Any] = {}
    total_ok = 0
    total_all = 0

    for tool_name, cases in all_cases.items():
        results = []
        for case in cases:
            results.append(await run_case(case))
        ok = sum(1 for r in results if r["status"] == "OK")
        total_ok += ok
        total_all += len(cases)
        summary[tool_name] = {"passed": ok, "total": len(cases), "cases": results}

    summary["_overall"] = {"passed": total_ok, "total": total_all}
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
