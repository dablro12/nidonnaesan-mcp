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
- `user_request` or `need_text` — 사용자 **한국어 원문 그대로** (필수 권장). 예: "서울쪽 레스토랑 협찬 추천해줘"
- `mode=easy_pick` — 협찬 처음 / 경쟁률 낮은 / 쉬운 협찬
- `mode=by_need` + need_text — 니즈 맞춤
- `mode=urgent` — 마감 하루 안 남은 / D-0 / D-1
- `sort_by=low_competition` — 경쟁 덜한 순 (NOT "competition")
- `table_format=compact` (default) — 4컬럼 표

FILTERS (if used): Korean only — region `서울|강남|부평`, category `맛집|숙박|뷰티`. English `Seoul/Western` works but need_text is better.

NEVER: filters만 쓰고 need_text 비우기 — always pass user_request.
NEVER: sort_by=`competition` — use `low_competition` or mode=`easy_pick`.
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
    "generate_application_comment": """
USE for: 신청 한마디 / 신청 문구 / 신청 메시지 써줘.

PARAMETERS (one of):
- `campaign_id` — 표의 id (`revu-1367756`, `cloudreview-233089`, 또는 숫자 `233089`)
- `product_name` — 제품명 (예: "텀블러 살균 건조기")
- `campaign_url` — 신청 링크 URL

`channel_url` is OPTIONAL. 없으면 캠페인·제품 정보로 초안 생성.
블로그 URL이 있으면 채널 맞춤 문구로 품질이 올라갑니다.
""".strip(),
    "analyze_channel_profile": """
USE for: 블로그 분석 / 채널 프로필 / 내 블로그 주제.
네이버 블로그 URL의 RSS로 주제·최근 글·블로거 유형을 분석합니다.
""".strip(),
    "get_campaign_link": """
USE for: 신청 링크 / apply url / 어디서 신청.
`campaign_id`는 표에 나온 `revu-숫자` 형식을 사용하세요.
""".strip(),
    "set_reviewer_profile": """
USE for: 프로필 저장 / 내 정보 저장 / 지역 업종 저장.
저장된 값은 이후 추천·팁·신청 문구에 기본 필터로 반영됩니다.
""".strip(),
    "get_reviewer_profile": """
USE for: 내 프로필 보여줘 / 저장된 설정 확인.
프로필이 없으면 적성 테스트를 먼저 안내합니다.
""".strip(),
}

TOOL_BASE_KO: dict[str, str] = {
    "get_campaign_recommendations": "협찬 통합 추천. 초보·니즈 맞춤·마감 임박·경쟁률 낮은 순으로 경쟁률·제품가격·신청 링크 표를 반환합니다.",
    "get_today_hot_campaigns": "오늘 신청자가 많은 인기 협찬 TOP N을 플랫폼별로 다양하게 표로 보여줍니다.",
    "search_campaigns_by_need": "사용자 문장(지역·업종·키워드)으로 협찬 캠페인을 자연어 검색합니다.",
    "get_urgent_campaigns": "D-0/D-1 마감 임박 협찬을 지역·필터와 함께 표로 반환합니다.",
    "compare_product_market_price": "네이버 쇼핑 시장가와 협찬 제공가·체험가치를 비교합니다.",
    "analyze_channel_profile": "네이버 블로그 URL로 채널 주제·스타일·최근 글을 분석합니다.",
    "generate_application_comment": "캠페인 ID·제품명·URL 기준 체험단 신청 한마디 3문장 초안을 생성합니다.",
    "get_campaign_link": "campaign_id를 기반으로 원본 협찬 신청 페이지 URL을 조회합니다.",
    "run_sponsorship_aptitude_test": "협찬 적성 테스트로 유형·추천 전략·다음 단계를 안내합니다.",
    "get_sponsorship_tips": "선정률·플랫폼·광고표기·SEO 등 검증된 협찬 선정 팁 29종을 제공합니다.",
    "set_reviewer_profile": "지역·업종·채널 URL 등 리뷰어 프로필을 저장해 추천에 반영합니다.",
    "get_reviewer_profile": "저장된 리뷰어 프로필과 필터 기본값을 조회합니다.",
}


def tool_description(base: str, chain_key: str) -> str:
    parts = [base.strip()]
    chain = CHAINS.get(chain_key, "")
    if chain:
        parts.append(chain)
    parts.append(TABLE_RULE)
    return "\n\n".join(parts)


def mcp_description(chain_key: str) -> str:
    """PlayMCP 마켓·심사 UI용 — 한 줄 기능 설명만 노출."""
    return TOOL_BASE_KO.get(chain_key, chain_key).strip()


def agent_tool_guide(chain_key: str) -> str:
    """에이전트 라우팅용 상세 가이드 (MCP description에는 넣지 않음)."""
    base = TOOL_BASE_KO.get(chain_key, chain_key)
    return tool_description(base, chain_key)
