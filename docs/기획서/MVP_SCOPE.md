# MVP 범위 정의

서비스: **nidonnaesan(니돈내산)**

## 포함 (Must Have)

| 기능 | 툴 | 비고 |
|------|-----|------|
| 오늘의 인기 협찬 | `get_today_hot_campaigns` | 기본 5건, 테이블 출력 |
| 니즈 기반 탐색 | `search_campaigns_by_need` | 3~5건 비교 |
| 시장가 비교 | `compare_product_market_price` | 네이버 쇼핑 API |
| 채널 분석 | `analyze_channel_profile` | 블로그 URL |
| 신청 한마디 | `generate_application_comment` | 3문장, skills 연동 |
| 신청 링크 | `get_campaign_link` | `originalUrl` |
| 적성 테스트 | `run_sponsorship_aptitude_test` | 1회성, 7문항 |
| 팁 전수 | `get_sponsorship_tips` | 5토픽 + auto |
| 프로필 저장 | `set_reviewer_profile` | Stateless + 영속 |
| 프로필 조회 | `get_reviewer_profile` | 필터 기본값 |

## 제외 (Out of Scope)

- Notion DB 저장
- `start_session` / 대화 세션 메모리
- heirmos식 풀 메모리 CRUD
- 100점 합격점수 (경쟁률 직관 표시로 대체)
- DEMO_SCRIPT / KPI 문서
- 마감 알림 푸시 (v1.1+)

## OAuth 단계

| Phase | 인증 | 프로필 저장 | 적합도 |
|-------|------|-------------|--------|
| Phase 1 (MVP 구현) | 없음 | `profile` 파라미터 fallback | 개발·로컬 테스트 |
| Phase 2 (PlayMCP 심사) | 카카오 OAuth | SQLite/Redis + `oauth_sub` | **권장** |

### Phase 1 동작

- LLM이 `set_reviewer_profile` 응답의 `profile` 객체를 다음 툴 호출에 전달
- 재방문 시 프로필 소실 가능 → 적성 테스트 재실행 안내

### Phase 2 동작

- OAuth Redirect: `https://playmcp.kakao.com/api/v1/applied-mcps/{mcpId}/authorize/oauth:callback`
- 개인정보 제3자 제공 동의 화면 권장
- `read_tip_ids`, `aptitude_type`, `channel_url` 영속 유지

## 프로필 저장 범위

| 필드 | 저장 | 용도 |
|------|------|------|
| `channel_url` | Y | 신청 문구, blog_index 팁 |
| `aptitude_type` | Y | 필터 프리셋, 팁 추천 |
| `preferred_media/category/type` | Y | 캠페인 검색 기본값 |
| `region` | Y | 방문형 캠페인 필터 |
| `experience_level` | Y | 팁 auto 순서 |
| `read_tip_ids` | Y | 순차 전수, 중복 방지 |
| 대화 히스토리 | N | 금지 |
| 캠페인 신청 이력 | N | v1.1+ |

## UI 카테고리 → API 매핑

| UI 카테고리 | API `category` | 비고 |
|------------|----------------|------|
| 맛집 | `맛집` | 1:1 |
| 뷰티 | `뷰티` | 1:1 |
| 숙박/여행 | `숙박` | API에 여행 없음 |
| 생활 | `생활` | 1:1 |
| 디지털 | `생활` + 키워드 | title/benefit 키워드 |
| 반려동물 | `생활` + 키워드 | 반려/펫/강아지/고양이 |
| 전체 | 필터 없음 | |

## 필터 체계

- **매체**: 블로그, 인스타그램, 유튜브, 블로그클립, 인스타릴스, 유튜브쇼츠, 전체
- **타입**: 방문형, 배송형, 기자단, 전체
- **플랫폼**: API 동적 목록 (레뷰, 리뷰노트, 티블 등)

## 데이터 소스

| 소스 | 용도 |
|------|------|
| 체험단 API `/campaigns` | 캠페인 목록/상세 |
| 네이버 쇼핑 API | 시장가 |
| `data/tips/*.json` | 팁 전수 (정적, <100ms) |

## 성공 기준 (MVP 검증)

- [ ] 10개 툴 스펙대로 MCP Inspector 통과
- [ ] 적성 테스트 → 프로필 → 맞춤 팁 → 캠페인 E2E
- [ ] 팁 5토픽 정상 로드
- [ ] 카카오 가이드 준수 (Stateless, 툴 10개, description 영문)

관련 문서:
- [PRD.md](./PRD.md)
- [TOOL_SPEC.md](./TOOL_SPEC.md)
- [VALIDATION.md](./VALIDATION.md)
