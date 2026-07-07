# 니돈내산 — PlayMCP 최종 제출

PlayMCP KC 컨테이너 등록, MCP 마켓 심사, AGENTIC PLAYER 10 예선 제출용 **최종 문서**입니다.

- 기술 배포: [DEPLOY_KC.md](../DEPLOY_KC.md)
- Tool 호출 예제: [PLAYMCP_EXAMPLES.md](../PLAYMCP_EXAMPLES.md)
- 카톡 스타일 테스트: [KAKAOTALK_TOOL_TESTS.md](../KAKAOTALK_TOOL_TESTS.md)
- 에이전트 라우팅: [MCP_CLIENT_ROUTING.md](../MCP_CLIENT_ROUTING.md)
- Tool 상세: [README.md](../../README.md) · [기능설명서.md](../기능설명서.md) · [TOOL_SPEC.md](../기획서/TOOL_SPEC.md)

---

## 1. MCP Container 정보 (KC)


| 항목           | 값                                                                    |
| ------------ | -------------------------------------------------------------------- |
| MCP 서버 이름    | `nidonnaesan-mcp-server`                                                    |
| 레지스트리 호스트    | `ghcr.io`                                                            |
| 이미지명         | `dablro12/nidonnaesan-mcp`                                           |
| 이미지 태그       | `latest`                                                             |
| MCP Endpoint | `https://nidonnaesan-mcp-server.playmcp-endpoint.kakaocloud.io/mcp` |


### MCP 설명 (KC / 이미지 등록 — 기능 설명란 복사용)

```
"협찬 받고, 추천까지 한 번에."

니돈내산은 카카오톡에서 협찬을 찾을 때 쓰는 도우미입니다.
"서울 맛집 협찬 있어?", "마감 임박한 거 알려줘", "경쟁 덜한 뷰티 협찬 추천해줘"처럼
말하면 맞는 협찬을 골라서 경쟁률·제품가격·신청 링크가 담긴 표로 보여줍니다.

• 인기 협찬, 내 조건 맞춤, 마감 임박 협찬 찾기
• 경쟁이 덜한 협찬부터 추천
• 네이버 쇼핑 가격 비교
• 선정 잘 되는 법, 플랫폼 고르는 법, 광고 표기 방법 등 팁
• 내 지역·관심 분야 저장해 두면 그에 맞게 목록 보여주기
• (부가) 블로그 보고 신청 문구 초안 만들기

직접 신청하고, 리뷰 쓰고, 광고 표기하는 건 본인이 해야 합니다.
이 서비스는 협찬 정보 추천과 문구 초안만 도와줍니다.
```

### MCP 설명 (짧은 버전 — 글자 수 제한 시)

```
카카오톡에서 "서울 맛집 협찬 있어?"처럼 물으면 맞는 협찬을 추천해 주는 도우미입니다.
인기·마감임박·경쟁 적은 협찬 추천, 가격 비교, 선정 팁을 제공합니다.
신청·리뷰·광고 표기는 사용자가 직접 합니다.
```

---

## 2. 심사 정보 (PlayMCP 마켓 등록)


| 항목               | 값                                                                    |
| ---------------- | -------------------------------------------------------------------- |
| **MCP 명**        | 니돈내산 - 협찬 받고, 추천까지 한 번에                                              |
| **MCP 식별자**      | `nidonnaesan` (코드: `nidonnaesan-mcp`)                                 |
| **인증 방식**        | 인증 사용하지 않음                                                           |
| **MCP Endpoint** | `https://nidonnaesan-mcp.playmcp-endpoint.kakaocloud.io/mcp` |


### 마켓 등록 한 줄 소개 (복사용)

```
카카오톡에서 말하듯이 맞는 협찬을 찾아 추천해 주는 협찬 도우미
```

### Tool 개수 (12개 — 카카오 권장 3~20개)


| #   | Tool                            | 기능 요약                                      |
| --- | ------------------------------- | ------------------------------------------ |
| 1   | `get_campaign_recommendations`  | **통합 추천** — 초보/니즈/마감임박, 4컬럼 표              |
| 2   | `get_today_hot_campaigns`       | 오늘의 인기 협찬                                 |
| 3   | `search_campaigns_by_need`      | 자연어 니즈 탐색 (지역·업종·마감)                       |
| 4   | `get_urgent_campaigns`          | 마감 임박 D-0/D-1                              |
| 5   | `compare_product_market_price`  | 네이버 쇼핑 시장가 비교                              |
| 6   | `analyze_channel_profile`       | 블로그 채널 분석                                 |
| 7   | `generate_application_comment`  | 신청 문구 초안 (부가 기능)                           |
| 8   | `get_campaign_link`             | 신청 페이지 링크                                  |
| 9   | `run_sponsorship_aptitude_test` | 협찬 적성 테스트                                  |
| 10  | `get_sponsorship_tips`          | 팁 전수 (29개)                                 |
| 11  | `set_reviewer_profile`          | 프로필 저장                                     |
| 12  | `get_reviewer_profile`          | 프로필 조회                                     |


### 대화 예시 (Starter Messages — 마켓 등록용)

1. 협찬 처음인데 뭐부터 해?
2. 경쟁률 낮은 협찬 5개 추천해줘
3. 오늘 인기 협찬 5개 보여줘
4. 서울쪽 레스토랑 협찬 추천해줘
5. 마감 하루 안 남은 협찬 알려줘
6. 부평 근처 숙박 체험단 있어?
7. 뷰티 배송형 협찬 중에 여유 있는 거 찾아줘
8. 강남 카페 방문형 협찬 추천해줘
9. 체험단 선정률 올리는 방법 알려줘
10. 처음인데 어느 체험단 사이트부터 할까?
11. 이 협찬 가격이랑 시장가 비교해줘

### 대화 예시 (심화 — 체이닝 테스트용)

```
협찬 처음인데 서울 맛집 5개 추천해줘
```

```
경쟁률 낮은 뷰티 협찬 찾아서 표로 보여줘
```

```
마감 임박한 협찬이랑 오늘 인기 협찬 둘 다 알려줘
```

### Tool 호출 예시 (PlayMCP 테스트)

**초보 추천 (4컬럼 표)**

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

---

## 3. 예선 제출 폼 (AGENTIC PLAYER 10)


| 항목                       | 내용                                                   |
| ------------------------ | ---------------------------------------------------- |
| 이름                       | 최대현                                                  |
| PlayMCP 서비스명             | **니돈내산 - 협찬 받고, 추천까지 한 번에**                         |
| [신청1] PlayMCP 상세 페이지 URL | *(제출 시 URL 입력)*                                      |
| 현재 소속 구분                 | 학교                                                   |
| 소속명                      | 서울대학교                                                |
| 소속 기관 홈페이지 URL           | [https://snuh.medisc.org/](https://snuh.medisc.org/) |


### 서비스 소개 및 지원 사유 (복사용)

```
니돈내산은 "검색"보다 "추천"에 집중합니다.

사용자가 카톡처럼 "협찬 처음인데 서울 맛집 추천해줘", "경쟁 덜한 뷰티 협찬 있어?"라고 말하면
여러 체험단 사이트를 돌아다닐 필요 없이 경쟁률·제품가격·신청 링크가 담긴 표로 바로 추천해 줍니다.

초보는 적성 테스트 후 easy_pick으로 시작하고, 지역·업종·마감 조건은 자연어로 입력하면 됩니다.
선정률·플랫폼·광고표기 팁도 함께 제공해 "찾기 → 고르기"까지 한 흐름으로 이어집니다.

신청·리뷰·광고 표기는 사용자 책임이며, 본 서비스는 협찬 정보 추천과 문구 초안을 돕습니다.
```

---

## 4. 배포 체크리스트

1. `main` push → GitHub Actions → `ghcr.io/dablro12/nidonnaesan-mcp:latest`
2. PlayMCP KC → 이미지 `latest` 재배포
3. PlayMCP 콘솔 → **「정보 불러오기」** → Tool 12개 확인
4. Starter Message로 위 대화 예시 테스트

---

## 5. 알려진 제한

- 캠페인 데이터는 제3자 API이며 Docker 빌드 시 동기화
- 네이버 API 미설정 시 시장가 비교 제한
- 프로필 저장은 지역·업종 등 필터 기본값 반영 (OAuth 없으면 단일 키 제한)
- 신청 문구는 초안이며 본인 채널에 맞게 수정 후 제출 필요

---

## 관련 문서


| 문서                                                    | 설명                |
| ----------------------------------------------------- | ----------------- |
| [PLAYMCP_EXAMPLES.md](../PLAYMCP_EXAMPLES.md)         | 카톡 스타일 예시        |
| [README.md](../../README.md)                          | 개요                |
| [DEPLOY_KC.md](../DEPLOY_KC.md)                       | KC 배포·Secrets     |
| [MCP_CLIENT_ROUTING.md](../MCP_CLIENT_ROUTING.md)     | 카톡 에이전트 라우팅      |
