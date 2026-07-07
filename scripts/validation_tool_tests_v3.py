#!/usr/bin/env python3
"""MCP v1.2 검증 — 통합 추천·compact 표·신청한마디 v2 (12툴×10)."""

from __future__ import annotations

import asyncio
import json
import random
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
load_dotenv(ROOT / ".env")

from application_comment import generate_comment
from aptitude_test import run_aptitude_test
from campaign_client import fetch_all_campaigns, fetch_campaign_by_id
from campaign_filters import hot_campaigns, search_by_need, urgent_campaigns
from campaign_formatter import campaigns_to_compact_markdown, campaigns_to_markdown
from campaign_recommender import recommend_campaigns
from campaign_resolver import resolve_campaign
from channel_profile import analyze_channel
from experience_value import enrich_campaign
from product_research import research_product_context
from naver_shopping import search_market_price
from profile_store import filter_defaults, get_profile, set_profile
from tips_loader import get_sponsorship_tip, load_tip

SAMPLE_BLOG = "https://blog.naver.com/dablro12"
DB_KEY = {"_user_key": "validation:v3"}


async def recommend(**kw):
    campaigns = await fetch_all_campaigns()
    profile = kw.pop("profile", None)
    f = kw.get("filters") or filter_defaults(get_profile(profile_fallback=profile) or profile or {})
    picked, meta = recommend_campaigns(
        campaigns,
        mode=kw.get("mode", "by_need"),
        need_text=kw.get("need_text"),
        top_n=kw.get("top_n", 5),
        filters=f,
        sort_by=kw.get("sort_by", "popular"),
        max_dday=kw.get("max_dday", 1),
        region=kw.get("region"),
    )
    rows = [enrich_campaign(c) for c in picked]
    fmt = kw.get("table_format", "compact")
    if fmt == "compact":
        md = campaigns_to_compact_markdown(rows, title=meta.get("mode", "rec"))
    else:
        md = campaigns_to_markdown(rows, title=meta.get("mode", "rec"))
    return {"mode": meta.get("mode"), "count": len(rows), "preview": md[:200]}


async def app_comment_v2(**kw):
    campaign, mode = await resolve_campaign(
        campaign_id=kw.get("campaign_id"),
        product_name=kw.get("product_name"),
        campaign_url=kw.get("campaign_url"),
    )
    if not campaign:
        raise ValueError("not found")
    url = kw.get("channel_url")
    if url:
        ch = await analyze_channel(url)
        if ch.get("error"):
            raise ValueError(ch["error"])
    else:
        from channel_profile import channel_from_campaign

        ch = channel_from_campaign(campaign)
    research = await research_product_context(campaign.get("title") or "")
    return generate_comment(
        campaign, ch, tone=kw.get("tone", "natural"), product_context=research.get("context")
    )


@dataclass
class Case:
    level: str
    name: str
    fn: Callable
    kwargs: dict[str, Any]
    expect_error: bool = False


def _preview(result: Any, max_len: int = 400) -> str:
    if isinstance(result, str):
        text = result
    else:
        text = json.dumps(result, ensure_ascii=False, indent=2)
    return text.replace("\n", " ")[:max_len]


async def run_case(case: Case) -> dict[str, Any]:
    try:
        fn = case.fn
        result = await fn(**case.kwargs) if asyncio.iscoroutinefunction(fn) else fn(**case.kwargs)
        status, err = "OK", None
    except Exception as exc:
        if case.expect_error:
            status, err, result = "OK", f"(expected) {exc.__class__.__name__}: {exc}", None
        else:
            status, err, result = "FAIL", f"{exc.__class__.__name__}: {exc}", None
    return {"level": case.level, "name": case.name, "status": status, "preview": _preview(result) if result else None, "error": err}


async def hot(**kw):
    campaigns = await fetch_all_campaigns()
    profile = kw.pop("profile", None)
    f = kw.get("filters") or filter_defaults(get_profile(profile_fallback=profile) or profile or {})
    rows = [enrich_campaign(c) for c in hot_campaigns(campaigns, filters=f, top_n=kw.get("top_n", 5))]
    return {"count": len(rows), "locations": [r.get("location_label") for r in rows[:3]]}


async def search(need_text, **kw):
    campaigns = await fetch_all_campaigns()
    profile = kw.pop("profile", None)
    f = kw.get("filters") or filter_defaults(get_profile(profile_fallback=profile) or profile or {})
    matched, kws, mode, intent = search_by_need(campaigns, need_text, top_n=kw.get("top_n", 5), filters=f)
    rows = [enrich_campaign(c) for c in matched]
    return {"mode": mode, "regions": intent.get("regions"), "categories": intent.get("categories"), "count": len(rows), "titles": [r["title"] for r in rows[:2]]}


async def urgent(**kw):
    campaigns = await fetch_all_campaigns()
    profile = kw.pop("profile", None)
    f = kw.get("filters") or filter_defaults(get_profile(profile_fallback=profile) or profile or {})
    region = kw.get("region")
    rows = [enrich_campaign(c) for c in urgent_campaigns(
        campaigns, top_n=kw.get("top_n", 5), max_dday=kw.get("max_dday", 1),
        filters=f, region=region,
    )]
    return {"count": len(rows), "ddays": [r.get("dDay") for r in rows[:5]], "titles": [r["title"] for r in rows[:2]]}


async def market_price(**kw):
    kw_val = kw.get("keyword")
    cid = kw.get("campaign_id")
    if cid:
        c = await fetch_campaign_by_id(cid)
        if not c and not kw_val:
            raise ValueError("not found")
        kw_val = kw_val or (c or {}).get("title", "")
    if not kw_val:
        raise ValueError("keyword required")
    m = await search_market_price(kw_val)
    return {"keyword": kw_val, "min": m.get("min_price"), "items": m.get("items_count")}


async def channel(url):
    return await analyze_channel(url)


async def app_comment(campaign_id, **kw):
    c = await fetch_campaign_by_id(campaign_id)
    if not c:
        raise ValueError("not found")
    url = kw.get("channel_url") or SAMPLE_BLOG
    ch = await analyze_channel(url)
    if ch.get("error"):
        raise ValueError(ch["error"])
    return generate_comment(c, ch, tone=kw.get("tone", "natural"))


async def link(campaign_id):
    if not str(campaign_id or "").strip():
        raise ValueError("id required")
    c = await fetch_campaign_by_id(campaign_id.strip())
    if not c:
        raise ValueError("not found")
    return {"url": c.get("originalUrl")}


def aptitude(answers):
    return run_aptitude_test(answers)


def tips(**kw):
    use_profile = kw.pop("use_profile", False)
    tip = get_sponsorship_tip(use_profile=use_profile, **kw)
    return {"tip_id": tip["tip_id"], "title": tip["title"][:60], "len": len(tip.get("sections_markdown", ""))}


def set_prof(**kw):
    profile = kw.pop("profile", DB_KEY)
    saved = set_profile({k: v for k, v in kw.items() if v is not None}, profile_fallback=profile)
    return {"region": saved.get("region"), "category": saved.get("preferred_category")}


def get_prof(profile=DB_KEY):
    stored = get_profile(profile_fallback=profile)
    return {"has": bool(stored), "filters": filter_defaults(stored or {})}


async def random_regional_link():
    campaigns = await fetch_all_campaigns()
    tagged = [c for c in campaigns if "[" in (c.get("title") or "") and "]" in (c.get("title") or "")]
    c = random.choice(tagged[:500] if len(tagged) > 500 else tagged)
    return await link(c["id"])


def tip_content_len():
    return {"count": len(load_tip("selection_rate")["sections_markdown"])}


async def build_cases() -> dict[str, list[Case]]:
    camps = await fetch_all_campaigns()
    seoul_food = next((c["id"] for c in camps if "서울" in (c.get("address") or "") and c.get("category") == "맛집"), camps[0]["id"])
    lodging = next((c["id"] for c in camps if c.get("category") == "숙박"), camps[0]["id"])

    return {
        "get_campaign_recommendations": [
            Case("simple", "easy_pick 초보", recommend, {"mode": "easy_pick"}),
            Case("medium", "by_need 서울 맛집", recommend, {"mode": "by_need", "need_text": "서울 맛집 협찬"}),
            Case("medium", "urgent D-1", recommend, {"mode": "urgent", "max_dday": 1}),
            Case("complex", "low_competition", recommend, {"mode": "by_need", "need_text": "카페", "sort_by": "low_competition"}),
            Case("complex", "부평 region", recommend, {"mode": "by_need", "need_text": "부평 숙박", "region": "부평"}),
            Case("simple", "compact top3", recommend, {"mode": "easy_pick", "top_n": 3}),
            Case("medium", "full table", recommend, {"mode": "by_need", "need_text": "뷰티", "table_format": "full"}),
            Case("complex", "프로필+니즈", recommend, {"mode": "by_need", "need_text": "방문형", "profile": {"region": "서울"}}),
            Case("medium", "urgent 서울", recommend, {"mode": "urgent", "region": "서울"}),
            Case("complex", "뷰티 배송 니즈", recommend, {"mode": "by_need", "need_text": "뷰티 배송형 협찬", "sort_by": "low_competition"}),
        ],
        "get_today_hot_campaigns": [
            Case("simple", "기본 5", hot, {}),
            Case("medium", "맛집 카테고리", hot, {"filters": {"category": "맛집"}}),
            Case("medium", "숙박 카테고리", hot, {"filters": {"category": "숙박"}}),
            Case("medium", "서울 region 필터", hot, {"filters": {"region": "서울"}}),
            Case("complex", "프로필 region 서울", hot, {"profile": {"region": "서울", "preferred_category": "맛집"}}),
            Case("complex", "방문형+맛집", hot, {"filters": {"type": "방문형", "category": "맛집"}}),
            Case("simple", "top_n=3", hot, {"top_n": 3}),
            Case("medium", "강남 region", hot, {"filters": {"region": "강남"}}),
            Case("complex", "인스타릴스", hot, {"filters": {"mediaType": "인스타릴스"}}),
            Case("complex", "뷰티 배송", hot, {"filters": {"category": "뷰티", "type": "배송형"}}),
        ],
        "search_campaigns_by_need": [
            Case("simple", "서울쪽 레스토랑", search, {"need_text": "서울쪽 레스토랑 협찬 추천해줘"}),
            Case("medium", "부평 숙박", search, {"need_text": "부평 근처 숙박 체험단"}),
            Case("medium", "수도권 카페", search, {"need_text": "수도권 카페 방문형"}),
            Case("medium", "강남 맛집", search, {"need_text": "강남 맛집 협찬"}),
            Case("complex", "제주 펜션", search, {"need_text": "제주 펜션 숙박 협찬"}),
            Case("complex", "마감임박 키워드", search, {"need_text": "마감 임박 뷰티 협찬"}),
            Case("simple", "강아지 간식", search, {"need_text": "강아지 간식 배송형"}),
            Case("medium", "이어폰 디지털", search, {"need_text": "무선 이어폰 디지털"}),
            Case("complex", "프로필+서울", search, {"need_text": "방문 체험", "profile": {"region": "서울", "preferred_category": "맛집"}}),
            Case("complex", "인천 부평 맛집", search, {"need_text": "인천 부평 맛집"}),
        ],
        "get_urgent_campaigns": [
            Case("simple", "D-1 기본", urgent, {}),
            Case("medium", "D-0만", urgent, {"max_dday": 0}),
            Case("medium", "top_n=10", urgent, {"top_n": 10}),
            Case("medium", "서울 region", urgent, {"region": "서울"}),
            Case("complex", "맛집+마감임박", urgent, {"filters": {"category": "맛집"}}),
            Case("complex", "부평 region", urgent, {"region": "부평"}),
            Case("simple", "재조회", urgent, {"top_n": 3}),
            Case("medium", "프로필 region", urgent, {"profile": {"region": "서울"}}),
            Case("complex", "숙박 카테고리", urgent, {"filters": {"category": "숙박"}}),
            Case("complex", "뷰티 배송", urgent, {"filters": {"category": "뷰티", "type": "배송형"}}),
        ],
        "compare_product_market_price": [
            Case("simple", "향수", market_price, {"keyword": "향수"}),
            Case("simple", "숙박 바우처", market_price, {"keyword": "호텔 숙박권"}),
            Case("medium", "캠페인ID", market_price, {"campaign_id": seoul_food}),
            Case("medium", "펜션", market_price, {"keyword": "제주 펜션"}),
            Case("complex", "캠페인+키워드", market_price, {"campaign_id": lodging, "keyword": "호텔"}),
            Case("complex", "영문", market_price, {"keyword": "lipstick"}),
            Case("simple", "강아지 사료", market_price, {"keyword": "강아지 사료"}),
            Case("medium", "에어프라이어", market_price, {"keyword": "에어프라이어"}),
            Case("complex", "invalid id", market_price, {"campaign_id": "fake-x"}, expect_error=True),
            Case("complex", "빈 입력", market_price, {}, expect_error=True),
        ],
        "analyze_channel_profile": [
            Case("simple", "dablro12", channel, {"url": SAMPLE_BLOG}),
            Case("medium", "m.blog", channel, {"url": "https://m.blog.naver.com/dablro12"}),
            Case("medium", "경로포함", channel, {"url": f"{SAMPLE_BLOG}/223562345678"}),
            Case("complex", "invalid", channel, {"url": "not-a-url"}),
            Case("complex", "empty path", channel, {"url": "https://blog.naver.com/"}),
            Case("simple", "naver blog", channel, {"url": "https://blog.naver.com/naver"}),
            Case("medium", "instagram", channel, {"url": "https://instagram.com/test"}),
            Case("medium", "youtube", channel, {"url": "https://youtube.com/@test"}),
            Case("complex", "example.com", channel, {"url": "https://example.com/blog"}),
            Case("complex", "no scheme", channel, {"url": "blog.naver.com/dablro12"}),
        ],
        "generate_application_comment": [
            Case("simple", "맛집 natural", app_comment_v2, {"campaign_id": seoul_food}),
            Case("medium", "product_name", app_comment_v2, {"product_name": "파스타"}),
            Case("medium", "polite", app_comment_v2, {"campaign_id": seoul_food, "tone": "polite"}),
            Case("medium", "숙박 appeal", app_comment_v2, {"campaign_id": lodging, "tone": "appeal"}),
            Case("complex", "invalid id", app_comment_v2, {"campaign_id": "nope"}, expect_error=True),
            Case("simple", "재생성", app_comment_v2, {"campaign_id": seoul_food, "tone": "natural"}),
            Case("medium", "lodging polite", app_comment_v2, {"campaign_id": lodging, "tone": "polite"}),
            Case("complex", "bad channel", app_comment_v2, {"campaign_id": seoul_food, "channel_url": "https://blog.naver.com/__none__"}, expect_error=True),
            Case("medium", "appeal food", app_comment_v2, {"campaign_id": seoul_food, "tone": "appeal"}),
            Case("complex", "no identifier", app_comment_v2, {}, expect_error=True),
            Case("medium", "제품명만", app_comment_v2, {"product_name": "텀블러 살균 건조기"}),
            Case("medium", "숫자 id만", app_comment_v2, {"campaign_id": "233089"}),
        ],
        "get_campaign_link": [
            Case("simple", "서울 맛집 ID", link, {"campaign_id": seoul_food}),
            Case("simple", "숙박 ID", link, {"campaign_id": lodging}),
            Case("medium", "랜덤 지역태그", random_regional_link, {}),
            Case("medium", "랜덤2", random_regional_link, {}),
            Case("medium", "랜덤3", random_regional_link, {}),
            Case("complex", "invalid", link, {"campaign_id": "bad-id"}, expect_error=True),
            Case("complex", "빈문자", link, {"campaign_id": ""}, expect_error=True),
            Case("simple", "재조회", link, {"campaign_id": seoul_food}),
            Case("medium", "랜덤4", random_regional_link, {}),
            Case("medium", "랜덤5", random_regional_link, {}),
        ],
        "run_sponsorship_aptitude_test": [
            Case("simple", "food_explorer", aptitude, {"answers": {"channel_type": "blog", "interest_category": "맛집", "region": "서울", "posting_frequency": "yes", "campaign_type_pref": "방문형", "sponsorship_experience": "no"}}),
            Case("simple", "traveler", aptitude, {"answers": {"channel_type": "blog", "interest_category": "여행", "region": "전국", "posting_frequency": "yes", "campaign_type_pref": "방문형", "sponsorship_experience": "yes"}}),
            Case("medium", "beauty", aptitude, {"answers": {"channel_type": "instagram", "interest_category": "뷰티", "region": "수도권", "posting_frequency": "yes", "campaign_type_pref": "배송형", "sponsorship_experience": "no"}}),
            Case("medium", "pet", aptitude, {"answers": {"channel_type": "blog", "interest_category": "반려", "region": "서울", "posting_frequency": "yes", "campaign_type_pref": "배송형", "sponsorship_experience": "no"}}),
            Case("complex", "none channel", aptitude, {"answers": {"channel_type": "none", "interest_category": "맛집", "region": "서울", "posting_frequency": "no", "campaign_type_pref": "상관없음", "sponsorship_experience": "no"}}),
            Case("complex", "youtube", aptitude, {"answers": {"channel_type": "youtube", "interest_category": "디지털", "region": "수도권", "posting_frequency": "yes", "campaign_type_pref": "배송형", "content_format": "video", "sponsorship_experience": "yes"}}),
            Case("medium", "life", aptitude, {"answers": {"channel_type": "blog", "interest_category": "생활", "region": "지방", "posting_frequency": "no", "campaign_type_pref": "배송형", "sponsorship_experience": "no"}}),
            Case("simple", "all_rounder", aptitude, {"answers": {"channel_type": "blog", "interest_category": "생활", "region": "전국", "posting_frequency": "yes", "campaign_type_pref": "상관없음", "sponsorship_experience": "yes"}}),
            Case("complex", "both format", aptitude, {"answers": {"channel_type": "blog", "interest_category": "맛집", "region": "서울", "posting_frequency": "yes", "campaign_type_pref": "방문형", "content_format": "both", "sponsorship_experience": "no"}}),
            Case("medium", "부평 region", aptitude, {"answers": {"channel_type": "blog", "interest_category": "맛집", "region": "지방", "posting_frequency": "yes", "campaign_type_pref": "방문형", "sponsorship_experience": "no"}}),
        ],
        "get_sponsorship_tips": [
            Case("simple", "selection_rate", tips, {"topic": "selection_rate"}),
            Case("medium", "AI 브리핑 query", tips, {"query": "AI 브리핑 인용 기준"}),
            Case("medium", "레뷰 등급 query", tips, {"query": "레뷰 등급 올리는 법"}),
            Case("medium", "사진 가이드", tips, {"topic": "photo_tips_by_category"}),
            Case("complex", "revu_grade_system", tips, {"topic": "revu_grade_system"}),
            Case("complex", "review_writing", tips, {"topic": "review_writing_guide"}),
            Case("simple", "platform", tips, {"topic": "platform"}),
            Case("medium", "광고표기 query", tips, {"query": "광고 표기 어떻게"}),
            Case("complex", "auto beginner", tips, {"topic": "auto", "profile": {"experience_level": "beginner", "read_tip_ids": []}, "use_profile": True}),
            Case("complex", "naver_seo", tips, {"topic": "naver_seo"}),
        ],
        "set_reviewer_profile": [
            Case("simple", "region 서울", set_prof, {"region": "서울"}),
            Case("medium", "region 부평+맛집", set_prof, {"region": "부평", "preferred_category": "맛집"}),
            Case("medium", "channel", set_prof, {"channel_url": SAMPLE_BLOG, "preferred_category": "맛집"}),
            Case("complex", "traveler profile", set_prof, {"aptitude_type": "traveler", "preferred_category": "숙박", "region": "전국"}),
            Case("complex", "full", set_prof, {"channel_url": SAMPLE_BLOG, "aptitude_type": "food_explorer", "preferred_category": "맛집", "preferred_type": "방문형", "region": "서울", "experience_level": "beginner"}),
            Case("simple", "read tips", set_prof, {"read_tip_ids": ["selection_rate", "platform"]}),
            Case("medium", "수도권", set_prof, {"region": "수도권"}),
            Case("complex", "beauty insta", set_prof, {"preferred_media": "인스타릴스", "preferred_category": "뷰티", "region": "서울"}),
            Case("medium", "intermediate", set_prof, {"experience_level": "intermediate"}),
            Case("simple", "all_rounder", set_prof, {"aptitude_type": "all_rounder"}),
        ],
        "get_reviewer_profile": [
            Case("simple", "after set", get_prof, {}),
            Case("medium", "filters region", get_prof, {}),
            Case("complex", "empty key", get_prof, {"profile": {"_user_key": "validation:v2:empty"}}),
            Case("simple", "재조회", get_prof, {}),
            Case("medium", "aptitude check", get_prof, {}),
            Case("complex", "other user", get_prof, {"profile": {"_user_key": "validation:v2:other"}}),
            Case("simple", "defaults", get_prof, {}),
            Case("medium", "category default", get_prof, {}),
            Case("complex", "region in filters", get_prof, {}),
            Case("simple", "final", get_prof, {}),
        ],
    }


async def main() -> None:
    cases = await build_cases()
    summary: dict[str, Any] = {}
    total_ok = total_all = 0
    for tool, tool_cases in cases.items():
        results = [await run_case(c) for c in tool_cases]
        ok = sum(1 for r in results if r["status"] == "OK")
        total_ok += ok
        total_all += len(tool_cases)
        summary[tool] = {"passed": ok, "total": len(tool_cases), "cases": results}
    summary["_overall"] = {"passed": total_ok, "total": total_all}
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if total_ok < total_all:
        raise SystemExit(1)


if __name__ == "__main__":
    asyncio.run(main())
