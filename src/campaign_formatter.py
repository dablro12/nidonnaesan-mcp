"""캠페인 테이블 마크다운 포맷."""

from __future__ import annotations

from typing import Any

TABLE_FOOTER = (
    "\n\n---\n"
    "_위 Markdown 표를 그대로 사용자에게 보여주세요. 목록 변환 금지._\n"
    "_가격: 제공가 또는 네이버 시장가. campaign_id는 `revu-숫자` 형식._"
)


def _price_cell(row: dict[str, Any]) -> str:
    if row.get("price_label"):
        return str(row["price_label"])
    provided = row.get("provided_value")
    if provided:
        return f"{provided:,}원"
    benefit = row.get("benefit") or ""
    if benefit and benefit != "상세페이지 참고":
        return benefit[:28]
    if row.get("market_price"):
        return str(row["market_price"])
    return "-"


def _comp_cell(row: dict[str, Any]) -> str:
    return row.get("competition_short") or row.get("competition") or "-"


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
        name = str(r.get("title", "-")).replace("|", "/")
        comp = _comp_cell(r).replace("|", "/")
        price = _price_cell(r).replace("|", "/")
        url = r.get("apply_url") or "-"
        link = f"[신청]({url})" if url != "-" else "-"
        lines.append(f"| {name} | {comp} | {price} | {link} |")
    lines.append(TABLE_FOOTER)
    return "\n".join(lines)


def campaigns_to_markdown(rows: list[dict[str, Any]], *, title: str = "협찬 캠페인") -> str:
    if not rows:
        return f"## {title}\n\n조건에 맞는 캠페인이 없습니다."

    lines = [
        f"## {title}",
        "",
        "| 플랫폼 | 제목 | 지역 | 카테고리 | 타입 | 매체 | 제공내역 | 경쟁률 | D-day | 제품가격 | 신청링크 |",
        "|--------|------|------|----------|------|------|----------|--------|-------|----------|----------|",
    ]
    for r in rows:
        dday = r.get("dDay", "-")
        url = r.get("apply_url") or "-"
        lines.append(
            f"| {r.get('platform','-')} | {r.get('title','-')} | {r.get('location_label','-')} "
            f"| {r.get('category','-')} | {r.get('type','-')} | {r.get('mediaType','-')} "
            f"| {r.get('benefit','-')} | {_comp_cell(r)} | D-{dday} | {_price_cell(r)} | [신청]({url}) |"
        )
    lines.append(TABLE_FOOTER)
    return "\n".join(lines)


def compare_to_markdown(data: dict[str, Any]) -> str:
    lines = [
        "## 시장가 비교",
        "",
        "| 항목 | 값 |",
        "|------|-----|",
        f"| 검색어 | {data.get('keyword', '-')} |",
    ]
    if data.get("campaign_id"):
        lines.append(f"| campaign_id | {data.get('campaign_id')} |")
    if data.get("platform"):
        lines.append(f"| 플랫폼 | {data.get('platform')} |")
    if data.get("title"):
        lines.append(f"| 협찬명 | {data.get('title')} |")
    if data.get("provided_value"):
        lines.append(f"| 협찬 제공가 | {data['provided_value']:,}원 |")
    elif data.get("benefit"):
        lines.append(f"| 제공내역 | {data.get('benefit')} |")
    min_p = data.get("min_price")
    max_p = data.get("max_price")
    if min_p and max_p:
        lines.append(f"| 네이버 시장가 | {min_p:,}~{max_p:,}원 |")
        if data.get("avg_price"):
            lines.append(f"| 평균가 | {data['avg_price']:,}원 |")
    if data.get("experience_value"):
        lines.append(f"| 체험가치 | {data.get('experience_value')} |")
    if data.get("notice"):
        lines.append(f"| 참고 | {data.get('notice')} |")
    lines.append(TABLE_FOOTER)
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
