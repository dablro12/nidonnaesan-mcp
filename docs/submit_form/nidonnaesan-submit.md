# 니돈내산(니돈내산) — PlayMCP 최종 제출

PlayMCP KC 컨테이너 등록, MCP 마켓 심사, AGENTIC PLAYER 10 예선 제출용 **최종 문서**입니다.

- 기술 배포: [DEPLOY_KC.md](../DEPLOY_KC.md)
- Tool 호출 예제: [PLAYMCP_EXAMPLES.md](../PLAYMCP_EXAMPLES.md)
- 카톡 스타일 테스트: [KAKAOTALK_TOOL_TESTS.md](../KAKAOTALK_TOOL_TESTS.md)
- 에이전트 라우팅: [MCP_CLIENT_ROUTING.md](../MCP_CLIENT_ROUTING.md)
- Tool 상세: [README.md](../../README.md) · [TOOL_SPEC.md](../기획서/TOOL_SPEC.md)

---

## 1. MCP Container 정보 (KC)


| 항목           | 값                                                                    |
| ------------ | -------------------------------------------------------------------- |
| MCP 서버 이름    | `nidonnaesan-mcp`                                                    |
| 레지스트리 호스트    | `ghcr.io`                                                            |
| 이미지명         | `dablro12/nidonnaesan-mcp`                                           |
| 이미지 태그       | `latest`                                                             |
| MCP Endpoint | `https://nidonnaesan-mcp.playmcp-endpoint.kakaocloud.io/mcp` |


### MCP 설명 (KC / 컨테이너용)

"협찬 받고, 신청까지 한 번에." **니돈내산**은 카카오톡처럼 말하듯이 물어보면 **맞는 협찬 찾기 → 체험가치·경쟁률 판단 → 신청 한마디**까지 이어주는 리뷰어 코파일럿 MCP입니다.

협찬이 처음이어도 적성 테스트와 초보 추천으로 시작할 수 있고, 지역·업종·마감임박 니즈를 자연어로 입력하면 4컬럼 슬림 표로 바로 신청할 수 있습니다.

- 오늘의 인기 협찬 · 니즈 맞춤 검색 · 마감 임박(D-0/D-1) 조회
- `get_campaign_recommendations` 통합 추천 — `easy_pick` / `by_need` / `urgent`, 경쟁률 낮은 순 정렬
- 네이버 쇼핑 시장가 비교 · 블로그 채널 분석 기반 **신청 한마디 3문장**
- blogreviewzip 검증 팁 28개+ (선정률·플랫폼·광고표기·네이버 SEO 등)
- 리뷰어 프로필 저장 (Stateless + set_profile)

체험단 신청·리뷰 작성·광고 표기 준수는 사용자 책임이며, 본 서비스는 **정보 안내**와 **문구 초안**을 제공합니다.

---

## 2. 심사 정보 (PlayMCP 마켓 등록)


| 항목               | 값                                                                    |
| ---------------- | -------------------------------------------------------------------- |
| **MCP 명**        | 니돈내산 - 협찬 받고, 신청까지 한 번에                                              |
| **MCP 식별자**      | `nidonnaesan` (코드: `nidonnaesan-mcp`)                                 |
| **인증 방식**        | 인증 사용하지 않음                                                           |
| **MCP Endpoint** | `https://nidonnaesan-mcp.playmcp-endpoint.kakaocloud.io/mcp` |


### Tool 개수 (12개 — 카카오 권장 3~20개)


| #   | Tool                            | 기능 요약                                      |
| --- | ------------------------------- | ------------------------------------------ |
| 1   | `get_campaign_recommendations`  | **통합 추천** — easy_pick / by_need / urgent, compact 표 |
| 2   | `get_today_hot_campaigns`       | 오늘의 인기 협찬 (신청자 수 기준)                        |
| 3   | `search_campaigns_by_need`      | 자연어 니즈 탐색 (지역·업종·마감 파싱)                     |
| 4   | `get_urgent_campaigns`          | 마감 임박 D-0/D-1 전용                             |
| 5   | `compare_product_market_price`  | 네이버 쇼핑 시장가 비교                              |
| 6   | `analyze_channel_profile`       | 블로그 채널 분석 (RSS)                             |
| 7   | `generate_application_comment`  | 신청 한마디 3문장 (ID·제품명·URL 해석)                  |
| 8   | `get_campaign_link`             | 신청 페이지 링크                                  |
| 9   | `run_sponsorship_aptitude_test` | 협찬 적성 테스트 (1회성)                             |
| 10  | `get_sponsorship_tips`          | 팁 전수 (28개+ index)                            |
| 11  | `set_reviewer_profile`          | 프로필 저장                                     |
| 12  | `get_reviewer_profile`          | 프로필·필터 기본값 조회                              |


### 데이터 출처


| 데이터      | 출처                                      |
| -------- | --------------------------------------- |
| 협찬 캠페인   | 체험단모음 API (`/campaigns`) — Docker 빌드 시 동기화 |
| 시장가      | 네이버 쇼핑 Search API (선택)                  |
| 채널 프로필   | 네이버 블로그 RSS                              |
| 협찬 팁     | blogreviewzip.com/tips + naver-seo (정적 MD) |
| 리뷰어 프로필 | SQLite (`data/profiles.db`)              |


### GitHub Actions Secrets (이미지 빌드)


| Secret                | 용도                |
| --------------------- | ----------------- |
| `NAVER_CLIENT_ID`     | 네이버 쇼핑 Search API |
| `NAVER_CLIENT_SECRET` | 네이버 쇼핑 Search API |


### 카카오 심사 정책 준수

- [x] Tool 12개 (3~20개)
- [x] Description 영·한, WHEN TO USE 가이드
- [x] "kakao" prefix/suffix 미사용
- [x] 개인정보 수집 없음 · 유료 결제 없음
- [x] 응답 limit 기본 5 (24k 미만)
- [x] 면책 문구 (신청·광고표기 사용자 책임)
- [x] 실패 응답 `isError: true` (MCP 권장)
- [x] pytest + validation v2/v3 (120 시나리오)

### 대화 예시 (Starter Messages)

1. 협찬 처음인데 뭐부터 해?
2. 오늘 인기 협찬 5개 보여줘
3. 서울쪽 레스토랑 협찬 추천해줘
4. 마감 하루 안 남은 협찬 5개 알려줘
5. 경쟁률 낮은 뷰티 협찬 찾아줘
6. 이 캠페인 체험가치 어때? 시장가랑 비교해줘
7. 블로그 blog.naver.com/xxx 기준으로 신청 한마디 써줘
8. 체험단 선정률 올리는 방법 알려줘
9. 처음인데 어느 체험단 사이트부터 할까?
10. 체험단 리뷰 광고 표기 어떻게 해?
11. 부평 근처 숙박 체험단 있어?

### Tool 호출 예시 (PlayMCP 테스트)

**초보 추천 (compact 4컬럼)**

```json
{
  "name": "get_campaign_recommendations",
  "arguments": {
    "mode": "easy_pick",
    "top_n": 5,
    "table_format": "compact"
  }
}
```

**니즈 + 경쟁률 낮은 순**

```json
{
  "name": "get_campaign_recommendations",
  "arguments": {
    "mode": "by_need",
    "need_text": "서울쪽 레스토랑 협찬",
    "sort_by": "low_competition",
    "table_format": "compact"
  }
}
```

**제품명으로 신청 한마디**

```json
{
  "name": "generate_application_comment",
  "arguments": {
    "product_name": "강남 파스타",
    "channel_url": "https://blog.naver.com/dablro12",
    "tone": "natural"
  }
}
```

---

## 3. 예선 제출 폼 (AGENTIC PLAYER 10)


| 항목                       | 내용                                                   |
| ------------------------ | ---------------------------------------------------- |
| 이름                       | 최대현                                                  |
| PlayMCP 서비스명             | **니돈내산 - 협찬 받고, 신청까지 한 번에**                         |
| [신청1] PlayMCP 상세 페이지 URL | *(제출 시 URL 입력)*                                      |
| 현재 소속 구분                 | 학교                                                   |
| 소속명                      | 서울대학교                                                |
| 소속 기관 홈페이지 URL           | [https://snuh.medisc.org/](https://snuh.medisc.org/) |


### 서비스 소개 및 지원 사유

니돈내산은 "검색"보다 "신청까지"에 집중합니다. 사용자가 카톡처럼 "협찬 처음인데 서울 맛집 추천해줘"라고내면, 여러 체험단 사이트를 돌아다닐 필요 없이 **경쟁률·체험가치·마감**을 한 표로 보여주고 **신청 한마디**까지 이어줍니다.

`get_campaign_recommendations`로 초보(`easy_pick`)·니즈 맞춤(`by_need`)·마감 임박(`urgent`)을 하나의 툴에서 처리하고, blogreviewzip 검증 팁 28개+와 네이버 SEO 가이드를 정적 지식으로 탑재했습니다. 신청·리뷰·광고 표기는 사용자 책임이며, 본 서비스는 정보 안내와 문구 초안을 돕습니다.

---

## 4. 배포 체크리스트

1. `main` push → GitHub Actions → `ghcr.io/dablro12/nidonnaesan-mcp:latest`
2. PlayMCP KC → 이미지 `latest` 재배포
3. PlayMCP 콘솔 → **「정보 불러오기」** → Tool 12개 확인
4. Starter Message로 [PLAYMCP_EXAMPLES.md](../PLAYMCP_EXAMPLES.md) 시나리오 테스트

---

## 5. 알려진 제한

- 캠페인 데이터는 제3자 API이며 Docker 빌드 시 동기화 (로컬 `campaigns.json` gitignore)
- 네이버 API 미설정 시 시장가·제품 맥락 조사 제한 (경고 문구)
- 신청 한마디는 초안이며 채널·캠페인에 맞게 수정 후 제출 필요
- SPA 캠페인 페이지 full crawl 미지원 — 제품명·네이버 쇼핑으로 맥락 보완

---

## 관련 문서


| 문서                                                    | 설명                |
| ----------------------------------------------------- | ----------------- |
| [PLAYMCP_EXAMPLES.md](../PLAYMCP_EXAMPLES.md)         | 카톡 스타일 예시 10개     |
| [README.md](../../README.md)                          | 개요                |
| [DEPLOY_KC.md](../DEPLOY_KC.md)                       | KC 배포·Secrets     |
| [MCP_CLIENT_ROUTING.md](../MCP_CLIENT_ROUTING.md)     | 카톡 에이전트 라우팅      |
