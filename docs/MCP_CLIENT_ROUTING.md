# 카카오톡 에이전트 MCP 라우팅 가이드

니돈내산 MCP를 카카오톡 에이전트에 연결할 때, 사용자 발화에 따라 **어떤 Tool을 먼저 호출할지** 정리한 문서입니다.

---

## 1. 우선순위 라우팅

| 사용자 의도 | 1순위 Tool | 2순위 (체이닝) |
|------------|-----------|---------------|
| 협찬 처음 / 뭐부터 | `run_sponsorship_aptitude_test` | `set_reviewer_profile` → `get_campaign_recommendations(mode=easy_pick)` |
| 추천 / 찾아줘 / 있어? | `get_campaign_recommendations` | `get_campaign_link` |
| 인기 / 핫 / TOP | `get_today_hot_campaigns` | `compare_product_market_price` |
| 지역+업종 니즈 | `get_campaign_recommendations(mode=by_need)` | `generate_application_comment` |
| 마감 / 급해 / D-day | `get_campaign_recommendations(mode=urgent)` 또는 `get_urgent_campaigns` | `get_campaign_link` |
| 경쟁률 낮은 / 여유 | `get_campaign_recommendations(sort_by=low_competition)` | — |
| 가격 / 가치 / 시장가 | `compare_product_market_price` | — |
| 신청 문구 / 한마디 | `generate_application_comment` | `analyze_channel_profile` |
| 팁 / 방법 / 선정률 | `get_sponsorship_tips` | — |
| 프로필 저장 | `set_reviewer_profile` | `get_reviewer_profile` |

---

## 2. `get_campaign_recommendations` 모드 선택

```
협찬 처음 / 초보 / 쉬운 것     → mode=easy_pick
~추천 / ~있어? / 니즈 문장      → mode=by_need + need_text=사용자 원문
마감 / 급해 / 오늘·내일 마감     → mode=urgent, max_dday=0~1
경쟁률 낮은 / 여유             → sort_by=low_competition
카톡 표 출력                   → table_format=compact (기본)
```

---

## 3. 신청 한마디 체이닝

1. 사용자가 캠페인 ID를 모를 때: `get_campaign_recommendations` → 표에서 관심 캠페인 확인
2. `generate_application_comment`에 `campaign_id` 또는 `product_name` 전달
3. `channel_url` 없으면 `get_reviewer_profile` → 없으면 사용자에게 블로그 URL 요청
4. 결과 하단 **확인 기준** 푸터를 사용자에게 안내

---

## 4. 초보 온보딩 플로우 (권장)

```
1. run_sponsorship_aptitude_test
2. set_reviewer_profile (결과 반영)
3. get_sponsorship_tips(topic=auto)
4. get_campaign_recommendations(mode=easy_pick, table_format=compact)
5. generate_application_comment (선택 캠페인)
```

---

## 5. 응답 형식 가이드

- **compact 표** (4컬럼): `협찬 제품명 | 경쟁률 | 제품가격 | 바로가기`
- **full 표** (11컬럼): 상세 비교가 필요할 때 `table_format=full`
- 신청 링크는 항상 `get_campaign_link`로 재확인 가능

---

## 6. 면책 (에이전트 응답 시 포함 권장)

> 체험단 신청·리뷰 작성·광고 표기는 [공정위 심사지침](https://www.ftc.go.kr)을 준수하세요. 신청 문구는 초안이며 본인 채널에 맞게 수정 후 제출하세요.
