"""협찬 팁 정적 데이터 로더."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

TIPS_DIR = Path(__file__).resolve().parent / "data" / "tips"

TOPIC_FILES = {
    "selection_rate": "selection-rate-7.json",
    "blog_index": "blog-index.json",
    "platform": "platform-guide.json",
    "ad_disclosure": "ad-disclosure.json",
    "posting_omission": "posting-omission.json",
}


def _load_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def load_index() -> dict[str, Any]:
    return _load_json(TIPS_DIR / "index.json")


def load_tip(topic_id: str) -> dict[str, Any]:
    filename = TOPIC_FILES.get(topic_id)
    if not filename:
        raise ValueError(f"Unknown tip topic: {topic_id}")
    return _load_json(TIPS_DIR / filename)


def sections_to_markdown(tip: dict[str, Any]) -> str:
    lines = [f"## {tip['title']}", "", tip.get("summary", "")]
    if tip.get("operator_note"):
        lines.extend(["", f"> **운영자 노트**: {tip['operator_note']}"])
    for section in tip.get("sections", []):
        lines.append("")
        lines.append(f"### {section.get('heading', '')}")
        lines.append(section.get("body", ""))
        for ex in section.get("examples", []):
            lines.append(f"- 예시: {ex}")
        for w in section.get("warnings", []):
            lines.append(f"- ⚠️ {w}")
    return "\n".join(lines)


def match_topic_by_query(query: str) -> str | None:
    q = query.lower()
    index = load_index()
    best_id: str | None = None
    best_score = 0
    for topic in index.get("topics", []):
        score = sum(1 for kw in topic.get("keywords", []) if kw in query or kw in q)
        if score > best_score:
            best_score = score
            best_id = topic["id"]
    return best_id


def auto_recommend_topic(
  profile: dict[str, Any] | None,
  read_tip_ids: list[str] | None = None,
) -> str | None:
    read = set(read_tip_ids or [])
    if profile:
        read.update(profile.get("read_tip_ids") or [])

    index = load_index()
    level = (profile or {}).get("experience_level", "none")
    order = index.get("auto_recommendation_order", {}).get(level) or index.get(
        "auto_recommendation_order", {}
    ).get("none", [])

    if profile and profile.get("channel_url") and "blog_index" not in read:
        if "blog_index" in order:
            pass
        else:
            order = list(order) + ["blog_index"]

    for topic_id in order:
        if topic_id not in read:
            return topic_id
    return None


def next_recommended_tip(current_id: str, read_tip_ids: list[str]) -> str | None:
    read = set(read_tip_ids)
    read.add(current_id)
    index = load_index()
    order = [t["id"] for t in sorted(index.get("topics", []), key=lambda t: t.get("priority", 99))]
    for topic_id in order:
        if topic_id not in read:
            return topic_id
    return None


def format_tip_response(
    tip: dict[str, Any],
    *,
    read_tip_ids: list[str] | None = None,
) -> dict[str, Any]:
    read = list(read_tip_ids or [])
    tip_id = tip["id"]
    return {
        "tip_id": tip_id,
        "title": tip["title"],
        "summary": tip.get("summary", ""),
        "operator_note": tip.get("operator_note", ""),
        "sections_markdown": sections_to_markdown(tip),
        "action_checklist": tip.get("action_checklist", []),
        "next_recommended_tip": next_recommended_tip(tip_id, read),
        "related_campaign_hint": tip.get("related_campaign_filter") or tip.get("related_tool"),
        "related_tool": tip.get("related_tool"),
    }


def get_sponsorship_tip(
    *,
    topic: str = "auto",
    query: str | None = None,
    profile: dict[str, Any] | None = None,
    use_profile: bool = True,
) -> dict[str, Any]:
    read_ids = list((profile or {}).get("read_tip_ids") or []) if use_profile else []
    matched: str | None = None

    if query:
        matched = match_topic_by_query(query)
        if matched:
            topic = matched

    if topic == "auto":
        if matched:
            topic = matched
        else:
            topic = auto_recommend_topic(profile if use_profile else None, read_ids) or "selection_rate"

    tip = load_tip(topic)
    return format_tip_response(tip, read_tip_ids=read_ids)
