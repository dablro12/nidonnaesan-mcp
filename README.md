<div align="center">

<img src="assets/app_icon.png" width="120" alt="니돈내산" />

# 니돈내산

### 협찬 받고, 신청까지 한 번에

<br>

[![PlayMCP](https://img.shields.io/badge/PlayMCP-사용_가능-FEE500?style=flat-square)](https://playmcp.kakaocloud.io)
[![AGENTIC PLAYER 10](https://img.shields.io/badge/카카오_2026-AGENTIC_PLAYER_10-000?style=flat-square&logo=kakaotalk&logoColor=FEE500)](https://playmcp.kakaocloud.io)

> 카카오톡에서 **한 마디**로 맞는 협찬을 찾고, 가치를 판단하고, 신청 문구까지 받는 리뷰어 코파일럿입니다.  
> **블로거 · 인스타 리뷰어 · 협찬 초보자** 모두 사용할 수 있습니다.

</div>

---

## MCP 소개

체험단모음 API와 운영자 검증 노하우를 바탕으로 **협찬 탐색 → 체험가치 판단 → 신청 한마디 → 팁 전수**까지 한 번에 돕는 MCP 서버입니다.

**핵심 기능**
- `get_campaign_recommendations` 통합 추천 — **초보(easy_pick)** · **니즈(by_need)** · **마감임박(urgent)**
- 4컬럼 슬림 표: `협찬 제품명 | 경쟁률 | 제품가격 | 바로가기`
- 지역·업종·마감 자연어 파싱 (`서울쪽 레스토랑 협찬` 등)
- 네이버 쇼핑 시장가 비교 + skill 기반 **신청 한마디 3문장**
- blogreviewzip **28개+ 팁** (선정률·플랫폼·광고표기·네이버 SEO)
- 협찬 적성 테스트 + 프로필 저장 (Stateless + set_profile)

**실사용 예시**  
카카오톡에서 「협찬 처음인데 서울 맛집 추천해줘」라고 물으면, AI가 **적성 테스트 → 경쟁률 낮은 캠페인 5개 → 신청 한마디**까지 한 번에 연결합니다.

---

## 이게 뭐예요?

여러 체험단 사이트를 매일 돌아다니며, 어떤 협찬이 내 채널에 맞는지, 가치가 있는지, 신청 메시지를 뭐라 쓸지 고민하지 않아도 됩니다.

**니돈내산**은 카카오톡 에이전트와 연결하면, 말하듯이 물어보기만 해도 **인기 협찬 목록**, **니즈 맞춤 검색**, **체험가치·시장가 비교**, **신청 한마디**, **선정률 올리는 팁**을 알려줍니다.

> 대신 신청·리뷰 작성·광고 표기 준수는 사용자 책임입니다. **정보 안내**와 **문구 초안**을 돕습니다.

---

## 이런 때 써보세요

| 상황 | 이렇게 물어보세요 |
|------|-------------------|
| 🆕 **협찬 처음** | 「협찬 적성 테스트 해줘」 |
| 🎯 **초보 추천** | 「경쟁률 낮은 협찬 5개 추천해줘」 |
| 🔥 **인기 협찬** | 「오늘 인기 협찬 5개 보여줘」 |
| 🔍 **니즈 탐색** | 「서울쪽 레스토랑 협찬 추천해줘」 |
| ⏰ **마감 임박** | 「마감 하루 안 남은 협찬 5개 알려줘」 |
| 📍 **지역 숙박** | 「부평 근처 숙박 체험단 있어?」 |
| 💰 **가치 판단** | 「이 캠페인 체험가치 어때? 시장가랑 비교해줘」 |
| ✍️ **신청 문구** | 「이 제품명으로 신청 한마디 써줘 블로그는 blog.naver.com/xxx」 |
| 📈 **선정률** | 「체험단 선정률 올리는 방법 알려줘」 |
| ⚖️ **광고 표기** | 「체험단 리뷰 광고 표기 어떻게 해?」 |

**한 번에 여러 가지**가 급하면 이렇게요:

> 「협찬 처음인데 서울 맛집 3개 골라주고 신청 문구까지 써줘」

---

## 어떻게 쓰나요?

### 카카오톡 · PlayMCP 사용자

1. PlayMCP에서 **니돈내산** MCP를 연결합니다.
2. 평소 카톡하듯 **니즈·채널·상황**을 한 문장으로 보냅니다.
3. 에이전트가 캠페인 테이블·신청 문구·팁을 알려줍니다.

**팁:** 블로그 URL을 프로필에 저장하면 매번 입력하지 않아도 됩니다.  
**팁:** 「적성 테스트 → 프로필 저장」 후 `easy_pick` 추천이 더 정확해집니다.

### 개발자 · MCP 연결

| 항목 | 값 |
|------|-----|
| Endpoint | `https://nidonnaesan-mcp.playmcp-endpoint.kakaocloud.io/mcp` |
| 식별자 | `nidonnaesan` |
| 이미지 | `ghcr.io/dablro12/nidonnaesan-mcp:latest` |

기술 문서 → [docs/DEPLOY_KC.md](docs/DEPLOY_KC.md) · [docs/PLAYMCP_EXAMPLES.md](docs/PLAYMCP_EXAMPLES.md) · [docs/MCP_CLIENT_ROUTING.md](docs/MCP_CLIENT_ROUTING.md)

---

## 바로 복사해서 써보기

```
협찬 처음인데 경쟁률 낮은 협찬 5개 추천해줘
```

```
오늘 인기 협찬 5개 보여줘
```

```
서울쪽 레스토랑 협찬 추천해줘
```

```
마감 하루 안 남은 협찬 5개 알려줘
```

```
체험단 선정률 올리는 방법 알려줘
```

더 많은 예시 → [카톡 스타일 테스트](docs/KAKAOTALK_TOOL_TESTS.md)

---

## MCP Tool 구성 (12개)

| Tool | 역할 |
|------|------|
| `get_campaign_recommendations` | **통합 추천** — easy_pick / by_need / urgent, compact 표 |
| `get_today_hot_campaigns` | 오늘의 인기 협찬 테이블 |
| `search_campaigns_by_need` | 자연어 니즈 기반 탐색 |
| `get_urgent_campaigns` | 마감 임박 D-0/D-1 |
| `compare_product_market_price` | 네이버 쇼핑 시장가 비교 |
| `analyze_channel_profile` | 블로그 채널 분석 |
| `generate_application_comment` | 신청 한마디 3문장 (ID·제품명·URL) |
| `get_campaign_link` | 신청 페이지 링크 |
| `run_sponsorship_aptitude_test` | 협찬 적성 테스트 |
| `get_sponsorship_tips` | 팁 전수 (28개+) |
| `set_reviewer_profile` | 프로필 저장 |
| `get_reviewer_profile` | 프로필 조회 |

---

## 사용하는 데이터 소스

| 구분 | 소스 | 용도 |
|------|------|------|
| 캠페인 | 체험단 API (`/campaigns`) | 목록·상세·신청링크 |
| 시장가 | 네이버 쇼핑 Search API | 가격 비교·제품 맥락 |
| 채널 | 네이버 블로그 RSS | 신청 문구용 프로필 |
| 팁 | `data/tips/` 정적 MD | 선정률·플랫폼·SEO 등 |
| 프로필 | SQLite | 적성·필터·팁 이력 |

---

## 로컬 실행

```bash
pip install -r requirements.txt
cp .env.example .env
python nidonnaesan_server.py
```

테스트: `pytest tests/ -q`

---

## 꼭 알아두세요

- 체험단 신청·리뷰 작성·광고 표기는 [공정위 심사지침](https://www.ftc.go.kr)을 준수하세요.
- 캠페인 데이터는 제3자 API이며, 실시간 정확도는 원본에 따릅니다.
- 신청 문구는 초안이며, 본인 채널에 맞게 수정 후 제출하세요.

---

## 더 보기

| 문서 | 내용 |
|------|------|
| [PRD](docs/기획서/PRD.md) | 제품 기획 |
| [TOOL_SPEC](docs/기획서/TOOL_SPEC.md) | MCP 툴 스펙 |
| [DEPLOY_KC](docs/DEPLOY_KC.md) | KC/GHCR 배포 |
| [nidonnaesan-submit.md](docs/submit_form/nidonnaesan-submit.md) | AGENTIC PLAYER 10 제출 |
| [MCP_CLIENT_ROUTING](docs/MCP_CLIENT_ROUTING.md) | 카톡 에이전트 라우팅 |

---

<div align="center">

**카카오 2026 AGENTIC PLAYER 10 · 예선 제출**

니돈내산 — 리뷰어를 위한 협찬 탐색·신청 코파일럿

</div>
