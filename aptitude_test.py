"""협찬 적성 테스트 로직."""

from __future__ import annotations

from typing import Any

APTITUDE_PRESETS: dict[str, dict[str, Any]] = {
    "food_explorer": {
        "aptitude_label": "맛집 탐험가",
        "summary": "방문형 맛집·카페 체험단에 강점이 있는 유형입니다.",
        "strategy": [
            "지역 맛집 방문형 캠페인부터 신청하세요.",
            "신청 메시지는 2~3문장으로 채우면 선정률이 올라갑니다.",
            "티블·리뷰플레이스처럼 경쟁률 중간 플랫폼부터 시작하세요.",
        ],
        "filter_preset": {"category": "맛집", "mediaType": "블로그", "type": "방문형"},
        "recommended_tip_topics": ["selection_rate", "platform"],
    },
    "beauty_creator": {
        "aptitude_label": "뷰티 크리에이터",
        "summary": "배송형 뷰티·인스타/릴스 중심 체험단에 적합합니다.",
        "strategy": [
            "배송형 뷰티 캠페인, 경쟁률 낮은 것부터 신청하세요.",
            "인스타 릴스 리뷰 스타일을 강조하세요.",
            "리뷰노트·링블 플랫폼을 우선 탐색하세요.",
        ],
        "filter_preset": {"category": "뷰티", "mediaType": "인스타릴스", "type": "배송형"},
        "recommended_tip_topics": ["selection_rate", "platform"],
    },
    "lifestyle_logger": {
        "aptitude_label": "생활 기록자",
        "summary": "생활·디지털 배송형 블로그 체험단에 적합합니다.",
        "strategy": [
            "생활/디지털 키워드 보조 필터로 탐색하세요.",
            "체험뷰·리뷰진에서 포트폴리오를 쌓으세요.",
            "블로그 일상 기록 스타일을 신청 메시지에 담으세요.",
        ],
        "filter_preset": {"category": "생활", "mediaType": "블로그", "type": "배송형"},
        "recommended_tip_topics": ["selection_rate", "blog_index"],
    },
    "traveler": {
        "aptitude_label": "여행러",
        "summary": "숙박·지역 방문형 체험단에 적합합니다.",
        "strategy": [
            "숙박·지역 체험 캠페인을 우선 탐색하세요.",
            "수도권 외 지역 캠페인도 기회가 많습니다.",
            "블로그+인스타 병행 리뷰를 강조하세요.",
        ],
        "filter_preset": {"category": "숙박", "mediaType": "블로그", "type": "방문형"},
        "recommended_tip_topics": ["platform", "selection_rate"],
    },
    "all_rounder": {
        "aptitude_label": "올라운더",
        "summary": "전 카테고리에서 경쟁률 낮은 캠페인부터 시작하는 유형입니다.",
        "strategy": [
            "체험뷰·리뷰진·티블에서 선정 경험을 쌓으세요.",
            "경쟁률 낮은 캠페인부터 신청하세요.",
            "적성 테스트 후 프로필을 저장해 맞춤 추천을 받으세요.",
        ],
        "filter_preset": {"category": "전체", "mediaType": "전체", "type": "전체"},
        "recommended_tip_topics": ["platform", "selection_rate"],
    },
}


def resolve_experience_level(answers: dict[str, Any]) -> str:
    if answers.get("channel_type") == "none":
        return "none"
    if answers.get("sponsorship_experience") == "no":
        return "none"
    if answers.get("posting_frequency") == "yes":
        return "intermediate"
    return "beginner"


def resolve_aptitude_type(answers: dict[str, Any]) -> str:
    if answers.get("channel_type") == "none" and answers.get("sponsorship_experience") == "no":
        return "all_rounder"
    category = answers.get("interest_category", "")
    mapping = {
        "맛집": "food_explorer",
        "뷰티": "beauty_creator",
        "여행": "traveler",
        "생활": "lifestyle_logger",
        "디지털": "lifestyle_logger",
        "반려": "lifestyle_logger",
    }
    return mapping.get(category, "all_rounder")


def run_aptitude_test(answers: dict[str, Any]) -> dict[str, Any]:
    aptitude_type = resolve_aptitude_type(answers)
    preset = APTITUDE_PRESETS[aptitude_type]
    experience_level = resolve_experience_level(answers)

    profile_payload = {
        "aptitude_type": aptitude_type,
        "preferred_category": preset["filter_preset"].get("category"),
        "preferred_media": preset["filter_preset"].get("mediaType"),
        "preferred_type": preset["filter_preset"].get("type"),
        "region": answers.get("region"),
        "experience_level": experience_level,
        "read_tip_ids": [],
    }

    return {
        "aptitude_type": aptitude_type,
        "aptitude_label": preset["aptitude_label"],
        "summary": preset["summary"],
        "strategy": preset["strategy"],
        "filter_preset": preset["filter_preset"],
        "profile_payload": profile_payload,
        "recommended_tip_topics": preset["recommended_tip_topics"],
        "next_action": "set_reviewer_profile",
    }
