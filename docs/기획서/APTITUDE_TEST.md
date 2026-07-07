# 협찬 적성 테스트 명세

## 개요

`run_sponsorship_aptitude_test`는 5~7개 질문 응답을 한 번에 받아 리뷰어 적성 유형과 맞춤 필터 프리셋을 반환하는 **1회성 Stateless 툴**이다. 세션 없이 동작하며, 결과는 `set_reviewer_profile`로 영속 저장한다.

## 질문 목록 (7문항)

| # | 질문 ID | 질문 | 선택지 | 필수 |
|---|---------|------|--------|------|
| 1 | `channel_type` | 주로 콘텐츠를 올리는 채널은? | `blog` / `instagram` / `youtube` / `none` | Y |
| 2 | `interest_category` | 관심 카테고리는? | `맛집` / `뷰티` / `생활` / `여행` / `디지털` / `반려` | Y |
| 3 | `region` | 주 활동 지역은? | `서울` / `수도권` / `지방` / `전국` | Y |
| 4 | `posting_frequency` | 주 1회 이상 포스팅이 가능한가? | `yes` / `no` | Y |
| 5 | `campaign_type_pref` | 방문형 vs 배송형 선호? | `방문형` / `배송형` / `상관없음` | Y |
| 6 | `content_format` | 사진 vs 영상 중 편한 것? | `photo` / `video` / `both` | N |
| 7 | `sponsorship_experience` | 협찬(체험단) 경험이 있나? | `yes` / `no` | Y |

## 입력 스키마

```json
{
  "answers": {
    "channel_type": "blog",
    "interest_category": "맛집",
    "region": "서울",
    "posting_frequency": "yes",
    "campaign_type_pref": "방문형",
    "content_format": "photo",
    "sponsorship_experience": "no"
  }
}
```

## 적성 유형 (5종)

| 유형 ID | 표시명 | 한 줄 설명 | 주요 신호 |
|---------|--------|-----------|----------|
| `food_explorer` | 맛집 탐험가 | 방문형 맛집·카페 체험단에 강점 | `interest_category=맛집` 또는 `campaign_type_pref=방문형` + 맛집 관심 |
| `beauty_creator` | 뷰티 크리에이터 | 배송형 뷰티·인스타/릴스 중심 | `interest_category=뷰티` + `instagram`/`video` |
| `lifestyle_logger` | 생활 기록자 | 생활·디지털 배송형 블로그 | `interest_category=생활`/`디지털`/`반려` |
| `traveler` | 여행러 | 숙박·지역 방문형 체험 | `interest_category=여행` |
| `all_rounder` | 올라운더 | 전 카테고리, 경쟁률 낮은 것부터 | `channel_type=none` 또는 복합 신호 |

## 유형 산출 규칙 (우선순위)

1. `channel_type=none` AND `sponsorship_experience=no` → `all_rounder`
2. `interest_category=맛집` → `food_explorer`
3. `interest_category=뷰티` → `beauty_creator`
4. `interest_category=여행` → `traveler`
5. `interest_category` ∈ {`생활`, `디지털`, `반려`} → `lifestyle_logger`
6. 그 외 → `all_rounder`

## 유형 → 필터 프리셋 매핑

| 유형 ID | `preferred_category` | `preferred_media` | `preferred_type` | `preferred_platform` | 시작 전략 |
|---------|---------------------|-------------------|------------------|---------------------|----------|
| `food_explorer` | `맛집` | `블로그` | `방문형` | `티블,리뷰플레이스,서울오빠` | 지역 맛집 방문형부터. 신청 메시지 2~3문장 필수. |
| `beauty_creator` | `뷰티` | `인스타릴스` | `배송형` | `리뷰노트,링블` | 배송형 뷰티, 경쟁률 낮은 캠페인 우선. |
| `lifestyle_logger` | `생활` | `블로그` | `배송형` | `체험뷰,리뷰진,티블` | 생활/디지털 키워드 보조 필터 적용. |
| `traveler` | `숙박` | `블로그` | `방문형` | `레뷰,리뷰플레이스` | 숙박·지역 체험 우선. 수도권 외 지역도 탐색. |
| `all_rounder` | `전체` | `전체` | `전체` | `체험뷰,리뷰진,티블` | 경쟁률 낮은 캠페인부터 포트폴리오 쌓기. |

## 출력 스키마

```json
{
  "aptitude_type": "food_explorer",
  "aptitude_label": "맛집 탐험가",
  "summary": "방문형 맛집·카페 체험단에 강점이 있는 유형입니다.",
  "strategy": [
    "지역 맛집 방문형 캠페인부터 신청하세요.",
    "신청 메시지는 2~3문장으로 채우면 선정률이 올라갑니다.",
    "티블·리뷰플레이스처럼 경쟁률 중간 플랫폼부터 시작하세요."
  ],
  "filter_preset": {
    "category": "맛집",
    "mediaType": "블로그",
    "type": "방문형",
    "platform": null
  },
  "profile_payload": {
    "aptitude_type": "food_explorer",
    "preferred_category": "맛집",
    "preferred_media": "블로그",
    "preferred_type": "방문형",
    "region": "서울",
    "experience_level": "none"
  },
  "recommended_tip_topics": ["selection_rate", "platform"],
  "next_action": "set_reviewer_profile"
}
```

## `experience_level` 매핑

| 조건 | 값 |
|------|-----|
| `sponsorship_experience=no` | `none` |
| `sponsorship_experience=yes` AND `posting_frequency=yes` | `intermediate` |
| `sponsorship_experience=yes` AND `posting_frequency=no` | `beginner` |
| `channel_type=none` | `none` |

## 후속 체이닝

1. `set_reviewer_profile(profile_payload)` — 프로필 저장
2. `get_sponsorship_tips(topic=auto)` — 맞춤 팁 전수
3. `search_campaigns_by_need(need_text="", filters=filter_preset, top_n=3)` — 추천 캠페인
