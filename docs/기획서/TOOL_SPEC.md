# 니돈내산 MCP Tool 스펙

서비스: **nidonnaesan(니돈내산)**  
툴 개수: **11개** (v1.1: `get_urgent_campaigns` 추가)  
전송: Streamable HTTP, Stateless (no session)

공통 규칙:
- `description`은 영문 + 서비스명 `nidonnaesan(니돈내산)` 병기
- `annotations`: `title`, `readOnlyHint`, `destructiveHint`, `openWorldHint`, `idempotentHint` 모두 지정
- 에러 시 마크다운 정제 텍스트 반환 (raw API 응답 금지)
- 응답 크기 최소화

프로필 연동: [PROFILE_MEMORY.md](./PROFILE_MEMORY.md)  
적성 테스트: [APTITUDE_TEST.md](./APTITUDE_TEST.md)  
팁 데이터: [data/tips/](../../data/tips/)

---

## 1. `get_today_hot_campaigns`

**description**: Returns today's most popular sponsorship campaigns from nidonnaesan(니돈내산) as a comparison table sorted by applicant count.

### inputSchema

```json
{
  "type": "object",
  "properties": {
    "top_n": { "type": "integer", "default": 5, "minimum": 1, "maximum": 20 },
    "filters": {
      "type": "object",
      "properties": {
        "mediaType": { "type": "string" },
        "type": { "type": "string", "enum": ["방문형", "배송형", "기자단", "전체"] },
        "platform": { "type": "string" },
        "category": { "type": "string" }
      }
    },
    "profile": { "type": "object", "description": "Fallback profile when OAuth unavailable" }
  }
}
```

### annotations

| field | value |
|-------|-------|
| title | Today's Hot Campaigns |
| readOnlyHint | true |
| destructiveHint | false |
| openWorldHint | true |
| idempotentHint | true |

### response

```json
{
  "campaigns": [
    {
      "id": "string",
      "platform": "레뷰",
      "title": "string",
      "category": "맛집",
      "type": "방문형",
      "mediaType": "블로그",
      "benefit": "string",
      "competition": "120/30 (4.0:1)",
      "competition_label": "치열",
      "dDay": 3,
      "experience_value": "보통",
      "market_price": null,
      "apply_url": "https://..."
    }
  ],
  "filters_applied": {},
  "total": 5
}
```

### 실패 처리

| 조건 | 응답 |
|------|------|
| API 타임아웃 | `error: CAMPAIGN_API_TIMEOUT`, 빈 목록 + 재시도 안내 |
| 필터 결과 0건 | `campaigns: []`, `message: 조건에 맞는 캠페인이 없습니다` |

---

## 1b. `get_urgent_campaigns` (v1.1)

**description**: Returns sponsorship campaigns with imminent deadlines (D-0/D-1) from nidonnaesan(니돈내산), sorted by urgency then applicant count.

### inputSchema

```json
{
  "type": "object",
  "properties": {
    "top_n": { "type": "integer", "default": 5 },
    "max_dday": { "type": "integer", "default": 1, "description": "0=today, 1=tomorrow" },
    "filters": { "type": "object", "properties": { "category": {}, "region": {}, "type": {} } },
    "profile": { "type": "object" },
    "region": { "type": "string", "description": "e.g. 서울, 부평, 수도권" }
  }
}
```

### annotations

| field | value |
|-------|-------|
| title | Urgent Deadline Campaigns |
| readOnlyHint | true |

---

## 2. `search_campaigns_by_need`

**description**: Searches sponsorship campaigns by natural-language need from nidonnaesan(니돈내산). Parses region (서울쪽, 부평) and category (레스토랑→맛집) from query. Returns 3-5 matched campaigns.

### inputSchema

```json
{
  "type": "object",
  "required": ["need_text"],
  "properties": {
    "need_text": { "type": "string", "description": "e.g. 아이가 놀 수 있는 튜브 협찬" },
    "top_n": { "type": "integer", "default": 5, "minimum": 3, "maximum": 10 },
    "filters": { "type": "object" },
    "profile": { "type": "object" }
  }
}
```

### annotations

| field | value |
|-------|-------|
| title | Search Campaigns by Need |
| readOnlyHint | true |
| destructiveHint | false |
| openWorldHint | true |
| idempotentHint | true |

### response

동일 테이블 컬럼 + `matched_keywords: ["튜브", "생활"]`, `relevance_score` (내부 정렬용, 선택 노출)

---

## 3. `compare_product_market_price`

**description**: Compares campaign product market price via Naver Shopping from nidonnaesan(니돈내산). Returns min/max/avg and experience value vs market.

### inputSchema

```json
{
  "type": "object",
  "properties": {
    "campaign_id": { "type": "string" },
    "keyword": { "type": "string", "description": "Used when campaign_id omitted" }
  },
  "oneOf": [
    { "required": ["campaign_id"] },
    { "required": ["keyword"] }
  ]
}
```

### annotations

| field | value |
|-------|-------|
| title | Compare Market Price |
| readOnlyHint | true |
| destructiveHint | false |
| openWorldHint | true |
| idempotentHint | true |

### response

```json
{
  "keyword": "string",
  "min_price": 15000,
  "max_price": 45000,
  "avg_price": 28000,
  "provided_value": 30000,
  "experience_value": "보통",
  "market_vs_provided": "시장 평균 대비 제공 가치 보통"
}
```

---

## 4. `analyze_channel_profile`

**description**: Analyzes reviewer channel URL from nidonnaesan(니돈내산) and extracts blog profile for application comment generation.

### inputSchema

```json
{
  "type": "object",
  "required": ["channel_url"],
  "properties": {
    "channel_url": { "type": "string", "format": "uri" }
  }
}
```

### response

```json
{
  "blog_name": "string",
  "main_categories": ["맛집"],
  "recent_topics": ["강남 카페"],
  "review_style": "솔직 후기, 직접 촬영",
  "recommended_media": "블로그"
}
```

---

## 5. `generate_application_comment`

**description**: Generates a 3-sentence Korean application comment for a campaign from nidonnaesan(니돈내산) using channel profile analysis.

### inputSchema

```json
{
  "type": "object",
  "required": ["campaign_id"],
  "properties": {
    "campaign_id": { "type": "string" },
    "channel_url": { "type": "string" },
    "tone": { "type": "string", "enum": ["natural", "polite", "appeal"], "default": "natural" },
    "profile": { "type": "object" }
  }
}
```

### response

```json
{
  "comment": "3문장 신청 문구",
  "channel_evidence": "채널 근거 1줄",
  "tips_reference": "selection_rate §1"
}
```

---

## 6. `get_campaign_link`

**description**: Returns the application page URL for a campaign from nidonnaesan(니돈내산).

### inputSchema

```json
{
  "type": "object",
  "required": ["campaign_id"],
  "properties": {
    "campaign_id": { "type": "string" }
  }
}
```

### annotations

| field | value |
|-------|-------|
| title | Get Campaign Link |
| readOnlyHint | true |
| destructiveHint | false |
| openWorldHint | true |
| idempotentHint | true |

### response

```json
{
  "campaign_id": "string",
  "apply_url": "https://...",
  "platform": "레뷰"
}
```

---

## 7. `run_sponsorship_aptitude_test`

**description**: Runs a one-shot sponsorship aptitude test from nidonnaesan(니돈내산). Returns reviewer type, filter preset, and profile_payload for saving.

### inputSchema

```json
{
  "type": "object",
  "required": ["answers"],
  "properties": {
    "answers": {
      "type": "object",
      "required": ["channel_type", "interest_category", "region", "posting_frequency", "campaign_type_pref", "sponsorship_experience"],
      "properties": {
        "channel_type": { "enum": ["blog", "instagram", "youtube", "none"] },
        "interest_category": { "enum": ["맛집", "뷰티", "생활", "여행", "디지털", "반려"] },
        "region": { "enum": ["서울", "수도권", "지방", "전국"] },
        "posting_frequency": { "enum": ["yes", "no"] },
        "campaign_type_pref": { "enum": ["방문형", "배송형", "상관없음"] },
        "content_format": { "enum": ["photo", "video", "both"] },
        "sponsorship_experience": { "enum": ["yes", "no"] }
      }
    }
  }
}
```

### annotations

| field | value |
|-------|-------|
| title | Sponsorship Aptitude Test |
| readOnlyHint | true |
| destructiveHint | false |
| openWorldHint | false |
| idempotentHint | true |

### response

[APTITUDE_TEST.md](./APTITUDE_TEST.md) 출력 스키마 참조.

---

## 8. `get_sponsorship_tips`

**description**: Delivers verified sponsorship coaching tips from nidonnaesan(니돈내산) static knowledge base. Supports topic-specific or auto-personalized delivery.

### inputSchema

```json
{
  "type": "object",
  "properties": {
    "topic": {
      "type": "string",
      "enum": ["selection_rate", "blog_index", "platform", "ad_disclosure", "posting_omission", "auto"],
      "default": "auto"
    },
    "query": { "type": "string", "description": "Natural language e.g. 선정률 올리는 법" },
    "use_profile": { "type": "boolean", "default": true },
    "profile": { "type": "object" }
  }
}
```

### annotations

| field | value |
|-------|-------|
| title | Sponsorship Tips |
| readOnlyHint | true |
| destructiveHint | false |
| openWorldHint | false |
| idempotentHint | true |

### response

```json
{
  "tip_id": "selection_rate",
  "title": "체험단 선정률 높이는 방법 7가지",
  "summary": "string",
  "operator_note": "string",
  "sections_markdown": "## 1. ...",
  "action_checklist": ["..."],
  "next_recommended_tip": "platform",
  "related_campaign_hint": "체험뷰·리뷰진 필터 추천",
  "related_tool": "generate_application_comment"
}
```

### topic=auto 규칙

1. `get_reviewer_profile` 또는 `profile` 파라미터 읽기
2. `read_tip_ids` 제외, `experience_level` 기반 `index.json` 순서 적용
3. `query` 있으면 `keywords` 매칭 우선

---

## 9. `set_reviewer_profile`

**description**: Saves or updates reviewer profile for nidonnaesan(니돈내산). Stateless — no session, profile persistence only.

### inputSchema

[PROFILE_MEMORY.md](./PROFILE_MEMORY.md) 참조.

### annotations

| field | value |
|-------|-------|
| title | Set Reviewer Profile |
| readOnlyHint | false |
| destructiveHint | false |
| openWorldHint | false |
| idempotentHint | true |

---

## 10. `get_reviewer_profile`

**description**: Retrieves saved reviewer profile and filter defaults from nidonnaesan(니돈내산).

### inputSchema

```json
{
  "type": "object",
  "properties": {
    "profile": { "type": "object" }
  }
}
```

### annotations

| field | value |
|-------|-------|
| title | Get Reviewer Profile |
| readOnlyHint | true |
| destructiveHint | false |
| openWorldHint | false |
| idempotentHint | true |

---

## 테이블 출력 표준 컬럼

| 컬럼 | 소스 | 설명 |
|------|------|------|
| 플랫폼 | `platform` | 체험단 사이트 |
| 제목 | `title` | 캠페인명 |
| 카테고리 | `category` | 맛집/뷰티/생활 등 |
| 타입 | `type` | 방문형/배송형/기자단 |
| 매체 | `mediaType` | 블로그/인스타릴스 등 |
| 제공 내역 | `benefit` | 체험 제공 가치 |
| 경쟁률 | `applicants/recruitCount` | N/M (X.X:1) |
| D-day | `dDay` | 마감까지 |
| 체험가치 | 계산값 | 높음/보통/낮음 |
| 시장가 | 네이버 쇼핑 | 최저~최고 (선택) |
| 신청 링크 | `originalUrl` | 클릭 이동 |

## 체험가치 기준

| 매체 | 기준 단가 |
|------|----------|
| 블로그 | 30,000원 |
| 인스타 릴스 | 50,000원 |
| 인스타 피드 | 40,000원 |
| 유튜브/쇼츠 | 50,000원 |
| 블로그클립 | 35,000원 |

`ratio = provided_value / benchmark`: ≥1.5 높음, ≥0.8 보통, <0.8 낮음

## 툴 체이닝 예시

```
run_sponsorship_aptitude_test → set_reviewer_profile → get_sponsorship_tips(auto) → search_campaigns_by_need
generate_application_comment ← get_sponsorship_tips(selection_rate)
```
