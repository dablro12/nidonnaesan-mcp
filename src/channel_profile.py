"""네이버 블로그 채널 프로필 분석."""

from __future__ import annotations

import re
from typing import Any
from xml.etree import ElementTree

import httpx

BLOGGER_TYPES = ("생활 블로거", "여행 블로거", "IT 블로거", "뷰티 블로거", "취미 블로거")

CATEGORY_HINTS: dict[str, list[str]] = {
    "맛집": ["맛집", "카페", "음식", "레스토랑", "식당"],
    "뷰티": ["뷰티", "화장품", "스킨케어", "메이크업"],
    "여행": ["여행", "숙박", "호텔", "캠핑"],
    "IT": ["IT", "테크", "디지털", "가전", "스마트"],
    "생활": ["생활", "일상", "리뷰", "쇼핑"],
}


def extract_blog_id(url: str) -> str | None:
    m = re.search(r"blog\.naver\.com/([^/?#]+)", url)
    return m.group(1) if m else None


async def fetch_blog_rss(blog_id: str) -> list[dict[str, str]]:
    url = f"https://rss.blog.naver.com/{blog_id}.xml"
    async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
        resp = await client.get(url)
        if resp.status_code != 200:
            return []
        root = ElementTree.fromstring(resp.content)

    items = []
    for item in root.findall(".//item")[:10]:
        title_el = item.find("title")
        cat_el = item.find("category")
        items.append(
            {
                "title": title_el.text if title_el is not None and title_el.text else "",
                "category": cat_el.text if cat_el is not None and cat_el.text else "",
            }
        )
    return items


def infer_categories(posts: list[dict[str, str]]) -> list[str]:
    text = " ".join(p["title"] + " " + p.get("category", "") for p in posts)
    found = []
    for cat, hints in CATEGORY_HINTS.items():
        if any(h in text for h in hints):
            found.append(cat)
    return found or ["생활"]


def infer_blogger_type(categories: list[str]) -> str:
    if "맛집" in categories:
        return "생활 블로거"
    if "뷰티" in categories:
        return "뷰티 블로거"
    if "여행" in categories:
        return "여행 블로거"
    if "IT" in categories:
        return "IT 블로거"
    return "생활 블로거"


def channel_from_campaign(campaign: dict[str, Any]) -> dict[str, Any]:
    """블로그 URL 없이 캠페인 메타만으로 신청 문구용 채널 프로필 생성."""
    category = campaign.get("category") or "생활"
    title = campaign.get("title") or ""
    main_categories = [category]
    blogger_type = "생활 블로거"

    if category == "숙박":
        main_categories = ["여행"]
        blogger_type = "여행 블로거"
    elif category == "뷰티":
        blogger_type = "뷰티 블로거"
    elif any(k in title for k in ("디지털", "가전", "IT", "스마트", "전자", "테크")):
        main_categories = ["IT", "생활"]
        blogger_type = "IT 블로거"

    product = re.sub(r"^\[[^\]]+\]\s*", "", title).strip() or "이 제품"

    return {
        "anonymous": True,
        "blog_name": "리뷰어",
        "main_categories": main_categories,
        "blogger_type": blogger_type,
        "review_style": "솔직한 경험 위주, 직접 촬영",
        "campaign_product": product,
        "recommended_media": campaign.get("mediaType") or "블로그",
    }


async def analyze_channel(channel_url: str) -> dict[str, Any]:
    blog_id = extract_blog_id(channel_url)
    if not blog_id:
        return {
            "error": "지원하지 않는 채널 URL입니다. 네이버 블로그 URL을 입력해주세요.",
            "channel_url": channel_url,
        }

    posts = await fetch_blog_rss(blog_id)
    categories = infer_categories(posts)
    recent_topics = [p["title"] for p in posts[:5] if p["title"]]

    return {
        "blog_id": blog_id,
        "blog_name": blog_id,
        "channel_url": channel_url,
        "main_categories": categories,
        "recent_topics": recent_topics,
        "review_style": "솔직한 경험 위주, 직접 촬영",
        "blogger_type": infer_blogger_type(categories),
        "recommended_media": "블로그",
    }
