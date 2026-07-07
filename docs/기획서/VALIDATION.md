# 검증 체크리스트

서비스: **nidonnaesan(니돈내산)**  
기준: [kakao_guide/](../../kakao_guide/), [MCP Best Practices](https://modelcontextprotocol.info/docs/best-practices/)

---

## 1. 카카오 PlayMCP 개발가이드 준수

| # | 항목 | 요구사항 | 니돈내산 대응 | 상태 |
|---|------|----------|--------------|------|
| K1 | MCP 스펙 버전 | 2025-03-26 ~ 2025-11-25 | SDK 선택 시 준수 | 구현 시 |
| K2 | 전송 방식 | Streamable HTTP only | HTTP MCP 서버 | 구현 시 |
| K3 | 서버 유형 | Remote, 공개 URL | 배포 시 공개 도메인 | 구현 시 |
| K4 | Stateless | no session 권장 | 세션 없음, 프로필만 저장 | **설계 완료** |
| K5 | 툴 이름 | A-Za-z0-9_- 만, 1~128자 | 10개 툴 모두 준수 | **설계 완료** |
| K6 | 툴 개수 | 3~10 권장, 20 초과 금지 | 10개 | **설계 완료** |
| K7 | 툴 스키마 | name, description, inputSchema, annotations | TOOL_SPEC.md 정의 | **설계 완료** |
| K8 | annotations | 5개 hint 모두 지정 | TOOL_SPEC.md 각 툴별 | **설계 완료** |
| K9 | description | 영문, 서비스명 병기, 1024자 이내 | nidonnaesan(니돈내산) 포함 | **설계 완료** |
| K10 | 툴명 kakao 금지 | prefix/suffix/포함 불가 | kakao 미사용 | **설계 완료** |
| K11 | 응답 크기 | 최소화, raw API 금지 | 정제된 테이블/마크다운 | **설계 완료** |
| K12 | 응답 속도 | avg 100ms, p99 3000ms | tips 정적 <100ms, API는 캐시 | 구현 시 |
| K13 | OAuth | 개인정보 시 Redirect URI 설정 | Phase 2 | 구현 시 |

## 2. MCP Best Practices 준수 점검

| # | 원칙 | 니돈내산 적용 | 바람직 여부 |
|---|------|--------------|------------|
| B1 | Single Responsibility | 협찬/체험단 코파일럿 단일 목적 | **적합** |
| B2 | Focused Tools (3~10) | 10개, 역할 분리 명확 | **적합** |
| B3 | Stateless Design | HTTP 무상태, 프로필만 영속 | **적합** |
| B4 | Configuration Externalized | `.env` API 키, `data/tips/` 정적 | **적합** |
| B5 | Fail-Safe / Graceful Degradation | API 실패 시 빈 목록+안내, tips는 항상 로컬 | **설계 완료** |
| B6 | Input Validation | JSON Schema per tool | **설계 완료** |
| B7 | Minimal Response Payload | 테이블 컬럼 표준화, raw campaigns 미반환 | **설계 완료** |
| B8 | No Monolithic Mega-Server | 캠페인/팁/프로필 툴 분리, 단일 서버 | **적합** |
| B9 | Security Layers | OAuth Phase 2, 입력 검증 | 구현 시 |
| B10 | Idempotent Read Tools | readOnlyHint=true 툴 다수 | **설계 완료** |

### 바람직하지 않은 패턴 (회피 확인)

| 패턴 | 회피 여부 |
|------|----------|
| 20개 초과 툴 | 회피 (10개) |
| start_session 세션 | 회피 |
| heirmos식 풀 메모리 CRUD | 회피 |
| raw API 응답 그대로 반환 | 회피 |
| 툴명에 kakao 포함 | 회피 |
| 광고 유도 응답 | 회피 |

---

## 3. 기능 E2E 검증

### 캠페인 API

- [ ] `GET /campaigns?limit=500` 목록 정상
- [ ] `GET /campaigns/{id}` 상세 정상
- [ ] 필터 4종 조합 (mediaType, type, platform, category)
- [ ] UI 카테고리 7종 매핑 (디지털/반려 키워드 보조)
- [ ] `originalUrl` 100% 존재

### 캠페인 툴

- [ ] `get_today_hot_campaigns` 5건 테이블
- [ ] `search_campaigns_by_need` 니즈 → 3~5건
- [ ] `compare_product_market_price` 최저/최고/평균
- [ ] 체험가치 라벨 (블로그 3만, 릴스 5만 기준)
- [ ] 경쟁률 N/M (X.X:1) + 여유/보통/치열

### 채널·신청

- [ ] `analyze_channel_profile` 블로그 URL 분석
- [ ] `generate_application_comment` 3문장 (skills 품질)
- [ ] `get_campaign_link` 링크 반환

### 적성 테스트

- [ ] 7문항 입력 → 5유형 중 1개 산출
- [ ] `profile_payload` 생성
- [ ] `filter_preset` 정확도 (APTITUDE_TEST.md 매핑표)

### 프로필 메모리

- [ ] `set_reviewer_profile` 저장/부분 업데이트
- [ ] `get_reviewer_profile` 조회 + filter_defaults
- [ ] 프로필 없을 때 적성 테스트 안내
- [ ] `read_tip_ids` append 및 중복 제거
- [ ] OAuth 없을 때 `profile` 파라미터 fallback

### 팁 전수

- [ ] `data/tips/` 5파일 + index.json 로드
- [ ] `get_sponsorship_tips(topic=selection_rate)` 섹션 출력
- [ ] `topic=auto` + `experience_level=none` → selection_rate 우선
- [ ] `read_tip_ids` 스킵 + `next_recommended_tip`
- [ ] `query` 키워드 매칭 ("광고 표기" → ad_disclosure)
- [ ] 응답 <100ms (정적 데이터)

### E2E 시나리오

- [ ] 적성 테스트 → set_profile → tips(auto) → search_campaigns
- [ ] selection_rate 팁 → generate_application_comment 체이닝
- [ ] platform 팁 → 체험뷰/리뷰진 필터 힌트

---

## 4. MCP Inspector 사전 점검 (구현 후)

- [ ] 10개 툴 등록 확인
- [ ] inputSchema 유효성
- [ ] annotations 5개 필드 존재
- [ ] tool call 성공/에러 응답 형식

---

## 5. 문서 산출물 완료 확인

| 문서 | 경로 | 상태 |
|------|------|------|
| PRD | docs/기획서/PRD.md | 완료 |
| MVP_SCOPE | docs/기획서/MVP_SCOPE.md | 완료 |
| TOOL_SPEC | docs/기획서/TOOL_SPEC.md | 완료 |
| APTITUDE_TEST | docs/기획서/APTITUDE_TEST.md | 완료 |
| PROFILE_MEMORY | docs/기획서/PROFILE_MEMORY.md | 완료 |
| VALIDATION | docs/기획서/VALIDATION.md | 완료 |
| tips index | data/tips/index.json | 완료 |
| tips 5토픽 | data/tips/*.json | 완료 |

---

## 6. 종합 판정

| 영역 | 판정 |
|------|------|
| 카카오 가이드 (설계) | **준수** |
| MCP Best Practices (설계) | **바람직** — SRP, Stateless, focused tools, minimal payload |
| set_profile vs Stateless | **양립** — 세션 없이 프로필만 저장, 지원금봇 패턴 |
| 구현 준비도 | 기획·스펙·데이터 완료, 2차 MCP 서버 구현 대기 |
