# 니돈내산 — PlayMCP 최종 제출

PlayMCP KC 컨테이너 등록, MCP 마켓 심사, AGENTIC PLAYER 10 예선 제출용 문서입니다.  
**README.md와 동일한 등록 정보**를 사용합니다.

---

## MCP-SERVER 등록폼 (KC)

| 항목 | 값 |
|------|-----|
| Status | Active |
| Endpoint name | `nidonnaesan-mcp-server` |
| Namespace | `kbm-u-4978960334` |
| **Endpoint URL** | `https://nidonnaesan-mcp-server.playmcp-endpoint.kakaocloud.io/mcp` |
| Registry | `ghcr.io/dablro12/nidonnaesan-mcp:latest` |
| GitHub | https://github.com/dablro12/nidonnaesan-mcp |

### Description (KC 기능 설명란)

```
"협찬 받고, 신청까지 한 번에."

협찬이 처음이어도 적성 테스트와 초보 추천으로 시작할 수 있고, 사용자의 니즈(지역·업종·마감임박 등)에 따라 자연어로 입력하면
협찬이 가능한 제품을 확인하고, 원하는 제품을 제공 받을 수 있도록 도와줄 수 있는 마케팅 분야 최초의 협찬 MCP입니다.
```

### Tool 소개 (등록폼)

1. **협찬 추천** — 오늘의 인기 · 니즈 맞춤 · 마감 임박 · 경쟁률 낮은 순 통합 추천
2. **가치 판단** — 네이버 쇼핑 시장가 비교 · 체험가치·경쟁률 표시
3. **신청 지원** — 제품명·캠페인 링크 기반 신청 한마디 3문장 (블로그 URL 선택)
4. **협찬 노하우** — 검증 팁 29종 (선정률·플랫폼·광고표기·SEO 등)
5. **내 정보 저장** — 지역·업종 프로필 · 적성 테스트

---

## MCP 서버 PlayMCP 등록 (마켓)

| 항목 | 값 |
|------|-----|
| **MCP 이름** | 니돈내산 - 협찬 받고, 추천까지 한 번에 |
| **MCP 식별자** | `nidonnaesan` |
| **인증** | 사용하지 않음 |
| **Endpoint** | `https://nidonnaesan-mcp-server.playmcp-endpoint.kakaocloud.io/mcp` |

### 설명 (마켓 등록 — 복사용)

니돈내산(협찬 받고, 추천까지 한 번에)은 협찬이 가능한 제품을 확인하고, 원하는 제품을 제공 받을 수 있도록 도와주는 **마케팅 분야 최초의 협찬 MCP**입니다.

카카오톡에서 "서울 맛집 협찬 있어?", "마감 임박한 거 알려줘", "경쟁 덜한 뷰티 추천해줘"처럼 말하면 맞는 협찬 제품을 골라 경쟁률·제품가격·신청 링크가 담긴 자료로 브랜드 협찬에 손쉽게 시도해볼 수 있습니다.

**주요 기능**

① 인기·니즈 맞춤·마감 임박 협찬 추천  
② 경쟁률 낮은 순 협찬 제품 추천  
③ 네이버 쇼핑 시장가·체험가치 비교  
④ 선정률·플랫폼·광고표기·SEO 등 팁 29종  
⑤ 지역·업종 프로필 저장 후 맞춤 적성 테스트와 신청 문구 초안  

이를 통해 여러 체험단 사이트를 돌아다니지 않아도 한곳에서 탐색·비교·선택이 가능하며, 블로거·인스타 리뷰어·협찬 초보 모두 사용할 수 있습니다.

**예시:** "오늘 인기 협찬 5개 보여줘"

### 대화 예시 (Starter Messages)

1. 협찬 처음인데 뭐부터 해?
2. 뷰티 배송형 협찬 중에 여유 있는 거 찾아줘
3. 체험단 선정률 올리는 방법 알려줘

---

## Tool 목록 (12개)

| # | Tool | 기능 |
|---|------|------|
| 1 | `get_campaign_recommendations` | 통합 추천 (초보/니즈/마감, 4컬럼 표) |
| 2 | `get_today_hot_campaigns` | 오늘의 인기 |
| 3 | `search_campaigns_by_need` | 자연어 니즈 |
| 4 | `get_urgent_campaigns` | 마감 임박 |
| 5 | `compare_product_market_price` | 시장가 비교 |
| 6 | `analyze_channel_profile` | 채널 분석 |
| 7 | `generate_application_comment` | 신청 한마디 |
| 8 | `get_campaign_link` | 신청 링크 |
| 9 | `run_sponsorship_aptitude_test` | 적성 테스트 |
| 10 | `get_sponsorship_tips` | 팁 29종 |
| 11 | `set_reviewer_profile` | 프로필 저장 |
| 12 | `get_reviewer_profile` | 프로필 조회 |

---

## 배포 체크리스트

1. `main` push → Actions CI + Docker `latest`
2. PlayMCP KC → `latest` 재배포
3. **정보 불러오기** → Tool 12개
4. Starter Message 3종 테스트

→ [DEPLOY_KC.md](../DEPLOY_KC.md)

---

## 관련 문서

| 문서 | 설명 |
|------|------|
| [README.md](../../README.md) | 개요·구조 |
| [기능설명서.md](../기능설명서.md) | 기능 상세 |
| [PLAYMCP_EXAMPLES.md](../PLAYMCP_EXAMPLES.md) | 카톡 예시 |
| [MCP_CLIENT_ROUTING.md](../MCP_CLIENT_ROUTING.md) | 에이전트 라우팅 |
