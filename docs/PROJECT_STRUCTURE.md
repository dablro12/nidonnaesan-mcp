# 프로젝트 구조 (PlayMCP Advanced MCP)

카카오 PlayMCP 개발가이드 및 `modu-emergencybell-mcp`와 동일한 **얇은 엔트리 + `src/` 도메인** 패턴을 따릅니다.

## 레이아웃

```
nidonnaesan-mcp/
├── nidonnaesan_server.py      # FastMCP 엔트리, @mcp.tool 12개
├── requirements.txt           # 런타임 의존성 (단일 소스)
├── Dockerfile                 # linux/amd64, 빌드 시 캠페인·팁 동기화
├── pyproject.toml             # pytest pythonpath
├── .env.example
├── src/                       # 비즈니스 로직 (flat import)
│   ├── __init__.py
│   ├── constants.py           # PlayMCP Endpoint·이름 상수
│   ├── campaign_client.py     # API + 메모리·디스크 캐시
│   ├── campaign_sync.py       # 시작 즉시 + 15분 백그라운드 동기화
│   ├── campaign_recommender.py
│   ├── filter_aliases.py      # 영문 필터 → 한국어 정규화
│   ├── application_comment.py
│   ├── channel_profile.py
│   ├── tool_descriptions.py   # PlayMCP WHEN TO USE / 체이닝
│   └── ...
├── data/
│   ├── campaigns/campaigns.json   # gitignore, 빌드·런타임 생성
│   └── tips/                      # index.json + *.md (29종)
├── scripts/
│   ├── sync_campaigns.py
│   ├── sync_blogreviewzip_tips.py
│   └── validation_*.py
├── tests/
└── docs/
```

## Import 규칙

- `nidonnaesan_server.py`가 `src/`를 `sys.path`에 추가
- 도메인 모듈은 `from campaign_client import ...` 형태 (패키지 prefix 없음)
- 테스트·CI: `PYTHONPATH=src:.` 또는 `pyproject.toml` `pythonpath`

## 런타임

| 환경 변수 | 기본값 | 설명 |
|-----------|--------|------|
| `MCP_HOST` | `0.0.0.0` | HTTP 바인드 |
| `MCP_PORT` | `8000` | PlayMCP 컨테이너 포트 |
| `CAMPAIGN_SYNC_INTERVAL_SEC` | `900` | 백그라운드 전체 수집 주기 |
| `CAMPAIGN_CACHE_TTL_SEC` | `900` | 메모리 캐시 TTL |
| `NAVER_CLIENT_ID/SECRET` | (없음) | 시장가 비교 (선택) |

## PlayMCP 등록 상수

`src/constants.py`와 문서·README가 동일한 값을 사용합니다.

- Endpoint: `https://nidonnaesan-mcp-server.playmcp-endpoint.kakaocloud.io/mcp`
- MCP ID: `nidonnaesan`

## 금지·주의

- 툴명에 `kakao` 포함 금지 (심사 반려)
- KC 이미지는 **linux/amd64** (GitHub Actions 빌드 사용)
- GHCR 패키지 **Public** 또는 KC에 PAT 필요
