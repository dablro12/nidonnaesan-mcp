"""캠페인 지역·업종 파싱 및 니즈 의도 추출."""

from __future__ import annotations

import re
from typing import Any

NON_REGION_TAGS = {
    "생활", "식품", "뷰티", "기자단", "블로그", "재택", "인스타", "릴스",
    "인스타/릴스", "유아", "테팔", "스스/블로그", "클립", "배송", "전국",
}

REGION_QUERY_ALIASES: dict[str, list[str]] = {
    "서울": ["서울", "서울쪽", "서울시"],
    "수도권": ["서울", "경기", "인천", "수도권"],
    "경기": ["경기", "경기도"],
    "인천": ["인천", "인천시"],
    "부평": ["부평", "인천 부평"],
    "강남": ["강남", "서울 강남"],
    "제주": ["제주", "제주도", "제주시"],
    "부산": ["부산", "부산시"],
    "대구": ["대구", "대구시"],
    "대전": ["대전", "대전시"],
    "광주": ["광주", "광주시"],
    "울산": ["울산", "울산시"],
    "지방": ["충북", "충남", "전북", "전남", "경북", "경남", "강원"],
}

CATEGORY_QUERY_ALIASES: dict[str, list[str]] = {
    "맛집": ["맛집", "레스토랑", "식당", "음식점", "먹거리", "요리"],
    "숙박": ["숙박", "펜션", "호텔", "리조트", "모텔", "게스트하우스"],
    "뷰티": ["뷰티", "화장품", "스킨케어", "메이크업"],
    "생활": ["카페", "생활", "용품", "가전"],
}

URGENT_PHRASES = ("마감 임박", "마감임박", "오늘 마감", "내일 마감", "마감 하루", "마감하루", "급한")


def _title_bracket(title: str) -> str | None:
    m = re.match(r"\[([^\]]+)\]", title or "")
    return m.group(1).strip() if m else None


def _is_region_tag(tag: str) -> bool:
    if not tag or tag in NON_REGION_TAGS:
        return False
    if any(x in tag for x in ("블로그", "릴스", "인스타", "기자단", "재택")):
        return False
    return True


def extract_location_tags(campaign: dict[str, Any]) -> list[str]:
    tags: list[str] = []
    title = campaign.get("title") or ""
    address = campaign.get("address") or ""
    region_field = campaign.get("region") or ""

    bracket = _title_bracket(title)
    if bracket and _is_region_tag(bracket):
        parts = re.split(r"[/\s]+", bracket)
        tags.extend(p for p in parts if p and p not in NON_REGION_TAGS)

    if region_field and region_field not in ("배송", "지역", "전국"):
        tags.append(region_field)

    for token in re.findall(r"(서울|경기|인천|부산|대구|대전|광주|울산|제주|강원|충북|충남|전북|전남|경북|경남)", address):
        if token not in tags:
            tags.append(token)

    for token in re.findall(
        r"(강남|강북|서초|마포|송파|부평|수원|화성|천안|청주|해운대|잠실|홍대|명동|동작|남구|북구|서구|중구)",
        f"{title} {address}",
    ):
        if token not in tags:
            tags.append(token)

    return tags


def location_label(campaign: dict[str, Any]) -> str:
    tags = extract_location_tags(campaign)
    if not tags:
        region = campaign.get("region") or ""
        if region == "배송":
            return "배송"
        if region == "전국":
            return "전국"
        return "-"
    return "·".join(tags[:3])


def expand_region_query(region: str) -> list[str]:
    region = region.strip()
    if not region:
        return []
    for key, aliases in REGION_QUERY_ALIASES.items():
        if region == key or region in aliases:
            return list(dict.fromkeys(aliases + [key]))
    return [region]


def match_region(campaign: dict[str, Any], region_tokens: list[str]) -> bool:
    if not region_tokens:
        return True
    haystack = " ".join(
        [
            campaign.get("title") or "",
            campaign.get("address") or "",
            campaign.get("region") or "",
            " ".join(extract_location_tags(campaign)),
        ]
    )
    return any(token in haystack for token in region_tokens)


def parse_need_intent(need_text: str) -> dict[str, Any]:
    text = need_text or ""
    regions: list[str] = []
    categories: list[str] = []
    filters: dict[str, Any] = {}
    max_dday: int | None = None

    for phrase in URGENT_PHRASES:
        if phrase in text.replace(" ", ""):
            max_dday = 1
            break

    for cat, aliases in CATEGORY_QUERY_ALIASES.items():
        if any(a in text for a in aliases):
            categories.append(cat)
            filters.setdefault("category", cat)

    for region_key, aliases in REGION_QUERY_ALIASES.items():
        if any(a in text for a in aliases):
            regions.extend(expand_region_query(region_key))
            break
    else:
        for token in re.findall(r"[가-힣]{2,}", text):
            if token in ("부평", "강남", "수원", "제주", "홍대", "잠실", "명동"):
                regions.extend(expand_region_query(token))

    regions = list(dict.fromkeys(regions))

    stop = {
        "협찬", "체험단", "리뷰", "찾아", "찾아줘", "알려줘", "해줘", "있어", "없어",
        "가지고", "오게", "해주", "보여", "추천", "검색", "관련", "가능", "원해",
        "근처", "쪽", "지역", "방문", "배송형", "방문형", "마감", "임박", "오늘", "내일",
        "하루", "안", "남은",
    }
    for cat_aliases in CATEGORY_QUERY_ALIASES.values():
        stop.update(cat_aliases)
    for region_aliases in REGION_QUERY_ALIASES.values():
        stop.update(region_aliases)

    keywords = [
        t
        for t in re.findall(r"[가-힣a-zA-Z0-9]+", text)
        if len(t) >= 2 and t not in stop
    ]

    return {
        "regions": regions,
        "categories": categories,
        "keywords": keywords,
        "max_dday": max_dday,
        "filters": filters,
    }


def enrich_campaign_location(campaign: dict[str, Any]) -> dict[str, Any]:
    tags = extract_location_tags(campaign)
    return {
        "location_tags": tags,
        "location_label": location_label(campaign),
    }
