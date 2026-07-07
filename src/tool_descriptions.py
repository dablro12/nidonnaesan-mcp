"""PlayMCP Tool description — WHEN TO USE / 표 출력 / 체이닝."""

from __future__ import annotations

TABLE_RULE = """
OUTPUT RULE (MANDATORY):
- Return the tool's Markdown table **as-is**. Do NOT convert to bullet lists or plain prose.
- Each campaign row must keep: 제품명, 경쟁률, 제품가격, 신청 링크.
- campaign_id format examples: `revu-1367756`, `gangnam-2229176` (NOT CMPN_xxx).
""".strip()

CHAINS = {
    "get_campaign_recommendations": """
USE FIRST for: 추천해줘, 찾아줘, 있어?, 경쟁률 낮은, 초보, 맞춤, 마감 임박 (unless only tips asked).

PARAMETERS:
- `mode=easy_pick` — 협찬 처음 / 경쟁률 낮은 / 쉬운 협찬
- `mode=by_need` + `need_text` — 사용자 **원문 그대로** (예: "서울쪽 레스토랑 협찬")
- `mode=urgent` — 마감 하루 안 남은 / D-0 / D-1
- `sort_by=low_competition` — 경쟁 덜한 순
- `table_format=compact` (default) — 4컬럼 표

NEVER: need_text 대신 filters만 쓰기 — "서울 맛집"은 need_text에 넣으세요.
NEVER: 경쟁률 낮은 요청에 mode=by_need만 쓰고 need_text 비우기 — `mode=easy_pick` 사용.
""".strip(),
    "get_today_hot_campaigns": """
USE for: 오늘 인기 / 핫 / TOP / 신청자 많은 협찬.
Returns Markdown table (compact). Platforms are diversified (not only 레뷰).
""".strip(),
    "search_campaigns_by_need": """
USE for: 지역+업종 자연어 탐색. Pass full user sentence as `need_text`.
Example: need_text="서울쪽 레스토랑 협찬 추천해줘"
""".strip(),
    "get_urgent_campaigns": """
USE for: 마감 임박 / 오늘 마감 / 내일 마감 / D-0 / D-1.
""".strip(),
    "compare_product_market_price": """
USE for: 시장가 비교 / 가격 비교 / 체험가치 / 이 협찬 가격.

PARAMETERS (priority):
1. `keyword` or `product_name` — 제품명 (가장 안정적)
2. `campaign_id` — 표에 나온 id (`revu-1367756` 형식)

NEVER: invent CMPN_xxx ids. If id unknown, use product name from the table title.
""".strip(),
    "get_sponsorship_tips": """
USE for: 선정률 / 플랫폼 / 광고표기 / 팁 / 방법 알려줘.

NEVER as only tool when user says 협찬 처음 — chain:
1) run_sponsorship_aptitude_test OR get_campaign_recommendations(mode=easy_pick)
2) then tips if needed.
""".strip(),
    "run_sponsorship_aptitude_test": """
USE FIRST when: 협찬 처음 / 뭐부터 해 / 입문 / 시작.
Then chain set_reviewer_profile + get_campaign_recommendations(mode=easy_pick).
""".strip(),
}


def tool_description(base: str, chain_key: str) -> str:
    parts = [base.strip()]
    chain = CHAINS.get(chain_key, "")
    if chain:
        parts.append(chain)
    parts.append(TABLE_RULE)
    return "\n\n".join(parts)
