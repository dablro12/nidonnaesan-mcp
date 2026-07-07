"""영문·별칭 필터값 → 한국어 API 필터 정규화."""

from __future__ import annotations

from typing import Any

REGION_ALIASES: dict[str, str] = {
    "seoul": "서울",
    "gangnam": "강남",
    "bupyeong": "부평",
    "incheon": "인천",
    "busan": "부산",
    "jeju": "제주",
    "gyeonggi": "경기",
    "suwon": "수원",
    "mapo": "마포",
    "jongno": "종로",
    "myeongdong": "명동",
    "hongdae": "홍대",
    "수도권": "수도권",
}

CATEGORY_ALIASES: dict[str, str] = {
    "western": "맛집",
    "korean": "맛집",
    "chinese": "맛집",
    "japanese": "맛집",
    "restaurant": "맛집",
    "food": "맛집",
    "cafe": "맛집",
    "coffee": "맛집",
    "맛집": "맛집",
    "accommodation": "숙박",
    "hotel": "숙박",
    "lodging": "숙박",
    "숙박": "숙박",
    "beauty": "뷰티",
    "뷰티": "뷰티",
    "lifestyle": "생활",
    "life": "생활",
    "생활": "생활",
    "digital": "생활",
    "pet": "생활",
}

TYPE_ALIASES: dict[str, str] = {
    "visit": "방문형",
    "visit_type": "방문형",
    "delivery": "배송형",
    "방문형": "방문형",
    "배송형": "배송형",
    "기자단": "기자단",
}

SORT_ALIASES: dict[str, str] = {
    "competition": "low_competition",
    "low": "low_competition",
    "low_competition": "low_competition",
    "popular": "popular",
    "urgent": "urgent",
}


def _alias_lookup(value: str, mapping: dict[str, str]) -> str:
    key = value.strip().lower().replace(" ", "")
    if key in mapping:
        return mapping[key]
    for alias, target in mapping.items():
        if alias in key or key in alias:
            return target
    return value.strip()


def localize_filters(filters: dict[str, Any] | None) -> dict[str, Any]:
    if not filters:
        return {}
    out: dict[str, Any] = {}
    for key, val in filters.items():
        if val is None or val == "" or val == "전체":
            continue
        text = str(val).strip()
        if key == "region":
            out["region"] = _alias_lookup(text, REGION_ALIASES)
        elif key == "category":
            out["category"] = _alias_lookup(text, CATEGORY_ALIASES)
        elif key == "type":
            out["type"] = _alias_lookup(text, TYPE_ALIASES)
        else:
            out[key] = text
    return out


def normalize_sort_by(sort_by: str | None) -> str:
    if not sort_by:
        return "popular"
    key = sort_by.strip().lower().replace(" ", "_")
    return SORT_ALIASES.get(key, sort_by)


def filters_to_need_text(filters: dict[str, Any]) -> str:
    parts: list[str] = []
    region = filters.get("region")
    category = filters.get("category")
    typ = filters.get("type")
    if region:
        parts.append(str(region))
    if category:
        parts.append(str(category))
    if typ:
        parts.append(str(typ))
    if not parts:
        return ""
    return " ".join(parts) + " 협찬 추천"
