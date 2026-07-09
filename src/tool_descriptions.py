"""PlayMCP Tool description — WHEN TO USE / 표 출력 / 체이닝."""

from __future__ import annotations

SERVICE_NAME = "니돈내산 - 협찬 받고, 추천까지 한 번에"
SERVICE_IDENTIFIER = f"nidonnaesan({SERVICE_NAME})"

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

TOOL_BASE_EN: dict[str, str] = {
    "get_campaign_recommendations": "Recommends sponsorship campaigns by need, ease, urgency, and competition with price and apply links",
    "get_today_hot_campaigns": "Returns today's popular sponsorship campaigns across platforms as a Markdown table",
    "search_campaigns_by_need": "Searches sponsorship campaigns from natural-language needs such as region, category, and keyword",
    "get_urgent_campaigns": "Returns campaigns closing soon, including D-0 and D-1 opportunities",
    "compare_product_market_price": "Compares market price, offered benefit, and experience value for a sponsored product",
    "analyze_channel_profile": "Analyzes a Naver Blog channel's topic, style, and recent posts",
    "generate_application_comment": "Generates a three-sentence application comment from a campaign, product, or URL",
    "get_campaign_link": "Returns the original application page URL for a campaign ID",
    "run_sponsorship_aptitude_test": "Runs a sponsorship aptitude test and suggests a reviewer strategy",
    "get_sponsorship_tips": "Returns practical sponsorship tips for selection, platforms, disclosure, and blog SEO",
    "set_reviewer_profile": "Saves reviewer profile preferences such as region, category, channel URL, and media type",
    "get_reviewer_profile": "Returns the saved reviewer profile and default campaign filters",
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
    base = TOOL_BASE_EN.get(chain_key, chain_key).strip().rstrip(".")
    return f"{base}. {SERVICE_IDENTIFIER}."


def agent_tool_guide(chain_key: str) -> str:
    """에이전트 라우팅용 상세 가이드 (MCP description에는 넣지 않음)."""
    base = TOOL_BASE_EN.get(chain_key, chain_key)
    return tool_description(base, chain_key)
