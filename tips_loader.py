"""협찬 팁 로더 — index.json 기반 Markdown 동적 로드."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

TIPS_DIR = Path(__file__).resolve().parent / "data" / "tips"

LEGACY_SLUG_MAP = {
    "selection_rate": "selection-rate-tips",
    "blog_index": "blog-index-explained",
    "platform": "platform-comparison",
    "ad_disclosure": "advertising-disclosure",
    "posting_omission": "posting-missing",
}


def _load_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def load_index() -> dict[str, Any]:
    return _load_json(TIPS_DIR / "index.json")


def _topic_index() -> dict[str, dict[str, Any]]:
    index = load_index()
    by_key: dict[str, dict[str, Any]] = {}
    for topic in index.get("topics", []):
        by_key[topic["id"]] = topic
        if topic.get("slug"):
            by_key[topic["slug"]] = topic
            by_key[topic["slug"].replace("-", "_")] = topic
    for legacy, slug in LEGACY_SLUG_MAP.items():
        if slug in by_key:
            by_key[legacy] = by_key[slug]
    return by_key


def _resolve_topic(topic_id: str) -> dict[str, Any]:
    topics = _topic_index()
    if topic_id in topics:
        return topics[topic_id]
    raise ValueError(f"Unknown tip topic: {topic_id}")


def _extract_operator_note(md: str) -> str:
    if "운영자 노트" in md:
        after = md.split("운영자 노트", 1)[-1]
        m = re.search(r"\*([^*]+)\*", after, re.DOTALL)
        if m:
            return m.group(1).strip()
    m = re.search(r"—[^\n]*\n\s*\*([^*]+)\*", md, re.DOTALL)
    return m.group(1).strip() if m else ""


def _extract_summary(md: str) -> str:
    lines = [ln.strip() for ln in md.splitlines() if ln.strip()]
    for ln in lines:
        if ln.startswith("#") or ln.startswith("**") or ln.startswith("-"):
            continue
        if len(ln) > 30:
            return ln[:300]
    return lines[1][:300] if len(lines) > 1 else ""


def load_tip(topic_id: str) -> dict[str, Any]:
    meta = _resolve_topic(topic_id)
    filename = meta.get("file") or f"{meta.get('slug', topic_id)}.md"
    path = TIPS_DIR / filename
    if not path.exists():
        raise ValueError(f"Tip file not found: {filename}")
    content = path.read_text(encoding="utf-8").strip()
    return {
        "id": meta["id"],
        "title": meta.get("title", topic_id),
        "summary": _extract_summary(content),
        "operator_note": _extract_operator_note(content),
        "sections_markdown": content,
        "action_checklist": meta.get("action_checklist", []),
        "keywords": meta.get("keywords", []),
        "category": meta.get("category"),
        "source": "markdown",
        "source_url": meta.get("source_url"),
    }


def sections_to_markdown(tip: dict[str, Any]) -> str:
    if tip.get("sections_markdown"):
        return tip["sections_markdown"]
    lines = [f"## {tip['title']}", "", tip.get("summary", "")]
    if tip.get("operator_note"):
        lines.extend(["", f"> **운영자 노트**: {tip['operator_note']}"])
    for section in tip.get("sections", []):
        lines.append("")
        lines.append(f"### {section.get('heading', '')}")
        lines.append(section.get("body", ""))
    return "\n".join(lines)


def match_topic_by_query(query: str) -> str | None:
    index = load_index()
    q = query.replace(" ", "")
    if "광고표기" in q or ("광고" in query and "표기" in query):
        return "ad_disclosure"
    if "누락" in query or "검색에서 사라" in query:
        return "posting_omission"
    if "선정률" in query:
        return "selection_rate"
    if "블로그지수" in q or "블로그 지수" in query:
        return "blog_index"
    if "레뷰등급" in q or "레뷰 등급" in query:
        return "revu_grade_system"
    if "AI브리핑" in q or "ai 브리핑" in query.lower():
        return "ai_briefing_review_guide"

    best_id: str | None = None
    best_score = 0
    for topic in index.get("topics", []):
        score = 0
        for kw in topic.get("keywords", []):
            if kw in query:
                score += max(2, len(kw))
        title = topic.get("title") or ""
        if title and any(part in query for part in title.split() if len(part) >= 3):
            score += 3
        if score > best_score:
            best_score = score
            best_id = topic["id"]
    return best_id if best_score > 0 else None


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
        order = list(order)
        if "blog_index" not in order:
            order.append("blog_index")

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
        "source": tip.get("source", "unknown"),
        "category": tip.get("category"),
        "source_url": tip.get("source_url"),
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
