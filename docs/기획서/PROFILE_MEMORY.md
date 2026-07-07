# 프로필 메모리 전략 (카카오 MCP 대회 기준)

## 설계 원칙

| 원칙 | 설명 |
|------|------|
| Stateless 서버 | HTTP 요청 간 서버 세션(`start_session`) 없음 |
| 프로필 영속 저장 | `set_reviewer_profile`로 사용자 컨텍스트만 저장 (지원금봇 패턴) |
| OAuth 키 | 카카오 OAuth `sub`를 저장 키로 사용 |
| Fallback | OAuth 없을 때 `profile` 파라미터를 매 툴 호출에 전달 |

카카오 PlayMCP 개발가이드는 **Stateless MCP 서버를 권장**하지만, **프로필 저장 자체는 금지하지 않음**. 지원금봇(`set_profile`), 청년줍줍(`recommend_for_profile`)이 동일 패턴으로 승인됨.

## 저장소

| 단계 | 저장소 | 키 |
|------|--------|-----|
| MVP (OAuth 없음) | 인메모리 / SQLite | `client_id` 헤더 또는 `profile` 파라미터 직접 전달 |
| 배포 (OAuth 연동) | SQLite 또는 Redis | `oauth_sub` (카카오 사용자 ID) |

## `set_reviewer_profile`

### 설명

Saves or updates the reviewer profile for nidonnaesan(니돈내산). Used after aptitude test, channel analysis, or tip reading. Stateless server — no session, profile only.

### 입력 스키마

```json
{
  "type": "object",
  "properties": {
    "channel_url": {
      "type": "string",
      "description": "Naver blog or Instagram URL"
    },
    "aptitude_type": {
      "type": "string",
      "enum": ["food_explorer", "beauty_creator", "lifestyle_logger", "traveler", "all_rounder"]
    },
    "preferred_media": {
      "type": "string",
      "description": "블로그, 인스타릴스, 유튜브 등"
    },
    "preferred_category": {
      "type": "string",
      "description": "맛집, 뷰티, 생활, 숙박, 전체"
    },
    "preferred_type": {
      "type": "string",
      "enum": ["방문형", "배송형", "기자단", "전체"]
    },
    "region": {
      "type": "string",
      "enum": ["서울", "수도권", "지방", "전국"]
    },
    "experience_level": {
      "type": "string",
      "enum": ["none", "beginner", "intermediate"]
    },
    "read_tip_ids": {
      "type": "array",
      "items": { "type": "string" },
      "description": "Already delivered tip IDs for sequential coaching"
    },
    "profile": {
      "type": "object",
      "description": "Fallback: full profile object when OAuth is not available"
    }
  }
}
```

### 동작

- 필드 단위 **merge** (부분 업데이트 허용)
- `read_tip_ids`는 **append** (중복 제거)
- OAuth 연동 시 `oauth_sub`로 upsert
- OAuth 없을 때: 응답에 저장된 `profile` 객체 반환 → LLM이 다음 툴 호출 시 `profile` 파라미터로 전달

### 출력

```json
{
  "status": "saved",
  "profile": {
    "channel_url": "https://blog.naver.com/example",
    "aptitude_type": "food_explorer",
    "preferred_media": "블로그",
    "preferred_category": "맛집",
    "preferred_type": "방문형",
    "region": "서울",
    "experience_level": "none",
    "read_tip_ids": ["selection_rate"],
    "updated_at": "2026-07-07T10:00:00Z"
  }
}
```

## `get_reviewer_profile`

### 설명

Retrieves the saved reviewer profile for nidonnaesan(니돈내산). Returns filter defaults for campaign search and tip recommendation.

### 입력

```json
{
  "profile": {
    "type": "object",
    "description": "Optional fallback profile when OAuth is not available"
  }
}
```

### 출력 (프로필 있음)

```json
{
  "has_profile": true,
  "profile": { "...": "..." },
  "filter_defaults": {
    "category": "맛집",
    "mediaType": "블로그",
    "type": "방문형"
  },
  "next_recommended_tip": "platform"
}
```

### 출력 (프로필 없음)

```json
{
  "has_profile": false,
  "message": "프로필이 없습니다. run_sponsorship_aptitude_test로 적성 테스트를 먼저 진행하세요.",
  "next_action": "run_sponsorship_aptitude_test"
}
```

## 다른 툴과의 연동

| 툴 | 프로필 활용 |
|----|------------|
| `get_today_hot_campaigns` | `filters` 미지정 시 `filter_defaults` 적용 |
| `search_campaigns_by_need` | `filters` 미지정 시 `filter_defaults` 적용 |
| `generate_application_comment` | `channel_url` 미지정 시 프로필에서 읽기 |
| `get_sponsorship_tips` | `topic=auto` 시 `experience_level`, `read_tip_ids`, `aptitude_type` 기반 추천 |
| `run_sponsorship_aptitude_test` | 결과 `profile_payload`를 `set_reviewer_profile`에 전달 |

## OAuth 단계별 전략

| 단계 | 인증 | 저장 | 재방문 |
|------|------|------|--------|
| Phase 1 (MVP) | 없음 | `profile` 파라미터 fallback | 대화 컨텍스트에 의존 |
| Phase 2 (심사/배포) | 카카오 OAuth | SQLite/Redis + `oauth_sub` | 프로필·팁 이력 유지 |

### OAuth Redirect URI

```
https://playmcp.kakao.com/api/v1/applied-mcps/{mcpId}/authorize/oauth:callback
```

## 금지 패턴

| 패턴 | 이유 |
|------|------|
| `start_session` / `end_session` | 카카오 가이드 Stateless 권장과 충돌 |
| heirmos식 풀 메모리 CRUD | MVP 범위 초과, 툴 개수 증가 |
| 대화 히스토리 서버 저장 | 개인정보·용량 리스크 |
