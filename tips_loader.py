"""협찬 팁 로더 — Markdown 우선, JSON fallback."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

TIPS_DIR = Path(__file__).resolve().parent / "data" / "tips"

TOPIC_MD_FILES: dict[str, str] = {
    "selection_rate": "체험단 선정률 높이는 방법 7가지.md",
    "blog_index": "블로그 지수란? 체험단 선정에 미치는 영향.md",
    "platform": "체험단 플랫폼 특징 총정리 (2026년 기준).md",
    "ad_disclosure": "체험단 후기 광고 표기법.md",
    "posting_omission": "[체험단 불이익 피하기] 포스팅 누락이란? 체험단 불이익 예방하는 법.md",
}

TOPIC_JSON_FILES: dict[str, str] = {
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


def _topic_meta(topic_id: str) -> dict[str, Any]:
    for topic in load_index().get("topics", []):
        if topic["id"] == topic_id:
            return topic
    return {"id": topic_id, "title": topic_id}


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
    return lines[0][:300] if lines else ""


def _load_from_markdown(topic_id: str) -> dict[str, Any] | None:
    filename = TOPIC_MD_FILES.get(topic_id)
    if not filename:
        return None
    path = TIPS_DIR / filename
    if not path.exists():
        return None
    content = path.read_text(encoding="utf-8").strip()
    if not content:
        return None
    meta = _topic_meta(topic_id)
    return {
        "id": topic_id,
        "title": meta.get("title", topic_id),
        "summary": _extract_summary(content),
        "operator_note": _extract_operator_note(content),
        "sections_markdown": content,
        "action_checklist": [],
        "keywords": meta.get("keywords", []),
        "source": "markdown",
    }


def load_tip(topic_id: str) -> dict[str, Any]:
    md_tip = _load_from_markdown(topic_id)
    if md_tip:
        return md_tip
    filename = TOPIC_JSON_FILES.get(topic_id)
    if not filename:
        raise ValueError(f"Unknown tip topic: {topic_id}")
    tip = _load_json(TIPS_DIR / filename)
    tip["source"] = "json"
    return tip


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
        for ex in section.get("examples", []):
            lines.append(f"- 예시: {ex}")
        for w in section.get("warnings", []):
            lines.append(f"- ⚠️ {w}")
    return "\n".join(lines)


def match_topic_by_query(query: str) -> str | None:
    index = load_index()
    best_id: str | None = None
    best_score = 0
    for topic in index.get("topics", []):
        score = sum(1 for kw in topic.get("keywords", []) if kw in query)
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
