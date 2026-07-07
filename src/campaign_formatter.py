"""캠페인 테이블 마크다운 포맷."""

from __future__ import annotations

from typing import Any


def campaigns_to_compact_markdown(rows: list[dict[str, Any]], *, title: str = "협찬 추천") -> str:
    """4컬럼 슬림 표: 협찬 제품명 | 경쟁률 | 제품가격 | 바로가기."""
    if not rows:
        return f"## {title}\n\n조건에 맞는 캠페인이 없습니다."

    lines = [
        f"## {title}",
        "",
        "| 협찬 제품명 | 경쟁률 | 제품가격 | 바로가기 |",
        "|-------------|--------|----------|----------|",
    ]
    for r in rows:
        name = r.get("title", "-")
        comp = r.get("competition", "-")
        price = r.get("provided_value")
        if price:
            price_str = f"{price:,}원"
        elif r.get("benefit") and r.get("benefit") != "상세페이지 참고":
            price_str = str(r.get("benefit", "-"))[:24]
        else:
            price_str = "-"
        url = r.get("apply_url") or "-"
        link = f"[신청]({url})" if url != "-" else "-"
        lines.append(f"| {name} | {comp} | {price_str} | {link} |")
    return "\n".join(lines)


def campaigns_to_markdown(rows: list[dict[str, Any]], *, title: str = "협찬 캠페인") -> str:
    if not rows:
        return f"## {title}\n\n조건에 맞는 캠페인이 없습니다."

    lines = [
        f"## {title}",
        "",
        "| 플랫폼 | 제목 | 지역 | 카테고리 | 타입 | 매체 | 제공내역 | 경쟁률 | D-day | 체험가치 | 신청링크 |",
        "|--------|------|------|----------|------|------|----------|--------|-------|----------|----------|",
    ]
    for r in rows:
        dday = r.get("dDay", "-")
        exp = r.get("experience_value", "-")
        url = r.get("apply_url") or "-"
        lines.append(
            f"| {r.get('platform','-')} | {r.get('title','-')} | {r.get('location_label','-')} "
            f"| {r.get('category','-')} | {r.get('type','-')} | {r.get('mediaType','-')} "
            f"| {r.get('benefit','-')} | {r.get('competition','-')} | D-{dday} | {exp} | [신청]({url}) |"
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
