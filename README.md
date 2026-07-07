# 니돈내산

### 협찬 받고, 추천까지 한 번에

[![PlayMCP](https://img.shields.io/badge/PlayMCP-Active-FEE500?style=flat-square)](https://playmcp.kakaocloud.io)
[![AGENTIC PLAYER 10](https://img.shields.io/badge/카카오_2026-AGENTIC_PLAYER_10-000?style=flat-square&logo=kakaotalk&logoColor=FEE500)](https://playmcp.kakaocloud.io)
[![GitHub](https://img.shields.io/badge/GitHub-dablro12%2Fnidonnaesan--mcp-181717?style=flat-square)](https://github.com/dablro12/nidonnaesan-mcp)

> 마케팅 분야 최초의 협찬 MCP — 카카오톡에서 말하듯이 협찬을 찾고, 비교하고, 신청까지 한 번에.

**블로거 · 인스타 리뷰어 · 협찬 초보자** 모두 사용할 수 있습니다.

---

## PlayMCP 등록 정보

| 항목 | 값 |
|------|-----|
| **MCP 이름** | 니돈내산 - 협찬 받고, 추천까지 한 번에 |
| **MCP 식별자** | `nidonnaesan` |
| **Endpoint** | `https://nidonnaesan-mcp-server.playmcp-endpoint.kakaocloud.io/mcp` |
| **Endpoint name** | `nidonnaesan-mcp-server` |
| **Docker 이미지** | `ghcr.io/dablro12/nidonnaesan-mcp:latest` |
| **GitHub** | https://github.com/dablro12/nidonnaesan-mcp |

### 한 줄 소개 (KC / 마켓 등록)

```
카카오톡에서 말하듯이 맞는 협찬을 찾아 추천해 주는 협찬 도우미
```

### 설명 (등록폼 복사용)

협찬이 처음이어도 적성 테스트와 초보 추천으로 시작할 수 있고, 사용자의 니즈(지역·업종·마감임박 등)에 따라 자연어로 입력하면 협찬이 가능한 제품을 확인하고, 원하는 제품을 제공 받을 수 있도록 도와줄 수 있는 **마케팅 분야 최초의 협찬 MCP**입니다.

카카오톡에서 「서울 맛집 협찬 있어?」, 「마감 임박한 거 알려줘」, 「경쟁 덜한 뷰티 추천해줘」처럼 말하면 맞는 협찬 제품을 골라 **경쟁률·제품가격·신청 링크**가 담긴 표로 보여줍니다.

---

## Tool 소개 (5가지)

1. **협찬 추천** — 오늘의 인기 · 니즈 맞춤 · 마감 임박(D-0/D-1) · 경쟁률 낮은 순 통합 추천
2. **가치 판단** — 네이버 쇼핑 시장가 비교 · 체험가치 · 경쟁률 표시
3. **신청 지원** — 제품명·캠페인 링크 기반 신청 한마디 3문장 (블로그 URL 있으면 채널 맞춤)
4. **협찬 노하우** — 운영자 검증 팁 **29종** (선정률·플랫폼·광고표기·네이버 SEO·리뷰 작성법 등)
5. **내 정보 저장** — 지역·업종 프로필 + 적성 테스트

### MCP Tool 목록 (12개)

| Tool | 역할 |
|------|------|
| `get_campaign_recommendations` | 통합 추천 — easy_pick / by_need / urgent |
| `get_today_hot_campaigns` | 오늘의 인기 협찬 |
| `search_campaigns_by_need` | 자연어 니즈 탐색 |
| `get_urgent_campaigns` | 마감 임박 D-0/D-1 |
| `compare_product_market_price` | 네이버 쇼핑 시장가 비교 |
| `analyze_channel_profile` | 블로그 채널 분석 |
| `generate_application_comment` | 신청 한마디 3문장 |
| `get_campaign_link` | 신청 페이지 링크 |
| `run_sponsorship_aptitude_test` | 협찬 적성 테스트 |
| `get_sponsorship_tips` | 팁 전수 (29개) |
| `set_reviewer_profile` | 프로필 저장 |
| `get_reviewer_profile` | 프로필 조회 |

---

## 대화 예시 (Starter Messages)

1. 협찬 처음인데 뭐부터 해?
2. 뷰티 배송형 협찬 중에 여유 있는 거 찾아줘
3. 체험단 선정률 올리는 방법 알려줘
4. 오늘 인기 협찬 5개 보여줘
5. 서울쪽 레스토랑 협찬 추천해줘
6. 디지털 가전 경쟁률 낮은 거 추천해줘
7. 텀블러 살균 건조기 신청한마디 작성해줘

---

## 프로젝트 구조 (PlayMCP Advanced MCP 패턴)

```
nidonnaesan-mcp/
├── nidonnaesan_server.py    # MCP 엔트리 (얇은 레이어, 12 tools)
├── requirements.txt
├── Dockerfile
├── src/                     # 도메인 로직
│   ├── campaign_*.py        # API·필터·추천·동기화
│   ├── application_comment.py
│   ├── channel_profile.py
│   ├── tool_descriptions.py
│   └── constants.py         # Endpoint·이름 등록 상수
├── data/
│   ├── campaigns/           # 캠페인 캐시 (런타임·빌드 시 동기화)
│   └── tips/                # 팁 MD 29종
├── scripts/                 # sync·validation
├── tests/
└── docs/                    # 배포·제출·기능설명서
```

상세 → [docs/PROJECT_STRUCTURE.md](docs/PROJECT_STRUCTURE.md)

---

## 로컬 실행

```bash
pip install -r requirements.txt
cp .env.example .env
python scripts/sync_campaigns.py   # 최초 1회
python nidonnaesan_server.py
```

- MCP Inspector: `http://localhost:8000/mcp`
- 테스트: `pytest tests/ -q`

---

## 배포

1. `main` push → GitHub Actions → `ghcr.io/dablro12/nidonnaesan-mcp:latest`
2. PlayMCP KC → 이미지 `latest` 재배포
3. **정보 불러오기** → Tool 12개 확인

→ [docs/DEPLOY_KC.md](docs/DEPLOY_KC.md)

---

## 데이터 소스

| 구분 | 소스 | 용도 |
|------|------|------|
| 캠페인 | 체험단 API | 목록·상세·신청링크 (15분 주기 동기화) |
| 시장가 | 네이버 쇼핑 API | 가격 비교 |
| 채널 | 네이버 블로그 RSS | 신청 문구 맞춤 (선택) |
| 팁 | `data/tips/` | 29종 정적 MD |
| 프로필 | SQLite | 필터·적성 |

---

## 꼭 알아두세요

- 체험단 **신청·리뷰·광고 표기**는 사용자 본인 책임입니다.
- 신청 문구는 **초안**이며, 본인 채널에 맞게 수정 후 제출하세요.
- 캠페인 데이터는 제3자 API 기준이며 실시간 정확도는 원본에 따릅니다.

---

## 문서

| 문서 | 내용 |
|------|------|
| [기능설명서](docs/기능설명서.md) | 서비스·기능 상세 |
| [submit_form/nidonnaesan-submit.md](docs/submit_form/nidonnaesan-submit.md) | PlayMCP·AGENTIC 제출 |
| [PLAYMCP_EXAMPLES.md](docs/PLAYMCP_EXAMPLES.md) | 카톡 스타일 예시 |
| [MCP_CLIENT_ROUTING.md](docs/MCP_CLIENT_ROUTING.md) | 에이전트 라우팅 |
| [DEPLOY_KC.md](docs/DEPLOY_KC.md) | KC/GHCR 배포 |

---

**카카오 2026 AGENTIC PLAYER 10 · 예선 제출**
