"""캠페인 테이블 마크다운 포맷."""

from __future__ import annotations

from typing import Any


def campaigns_to_markdown(rows: list[dict[str, Any]], *, title: str = "협찬 캠페인") -> str:
    if not rows:
        return f"## {title}\n\n조건에 맞는 캠페인이 없습니다."

    lines = [
        f"## {title}",
        "",
        "| 플랫폼 | 제목 | 카테고리 | 타입 | 매체 | 제공내역 | 경쟁률 | D-day | 체험가치 | 신청링크 |",
        "|--------|------|----------|------|------|----------|--------|-------|----------|----------|",
    ]
    for r in rows:
        dday = r.get("dDay", "-")
        exp = r.get("experience_value", "-")
        url = r.get("apply_url") or "-"
        lines.append(
            f"| {r.get('platform','-')} | {r.get('title','-')} | {r.get('category','-')} "
            f"| {r.get('type','-')} | {r.get('mediaType','-')} | {r.get('benefit','-')} "
            f"| {r.get('competition','-')} | D-{dday} | {exp} | [신청]({url}) |"
        )
    return "\n".join(lines)


def dict_to_markdown(data: dict[str, Any]) -> str:
    lines = []
    for key, val in data.items():
        if isinstance(val, list):
            lines.append(f"**{key}**:")
            for item in val:
                lines.append(f"- {item}")
        elif isinstance(val, dict):
            lines.append(f"**{key}**: {val}")
        else:
            lines.append(f"**{key}**: {val}")
    return "\n".join(lines)
