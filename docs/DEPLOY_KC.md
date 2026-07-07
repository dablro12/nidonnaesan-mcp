# PlayMCP in KC 배포 가이드 (니돈내산)

## 1. GitHub Actions 확인

https://github.com/dablro12/nidonnaesan-mcp/actions

- **CI** → 테스트 통과
- **Publish Docker image** → ✅ success 여야 함

---

## 2. GHCR 패키지 공개

GHCR 이미지가 **private**이면 KC가 pull 못 해서 **Starting에서 실패**합니다.

1. https://github.com/dablro12?tab=packages
2. **nidonnaesan-mcp** 클릭
3. **Package settings** → **Change visibility** → **Public**

Private 유지 시 KC에 `read:packages` PAT 입력.

---

## 3. KC 이미지 등록

https://playmcp.kakaocloud.io → **+ 새 MCP 서버 등록** → **이미지 등록**

| 항목 | 값 |
|------|-----|
| MCP 서버 이름 | `nidonnaesan-mcp-server` |
| 설명 | `니돈내산 - 협찬 받고, 추천까지 한 번에` |
| Registry 호스트 | `ghcr.io` |
| image_name | `dablro12/nidonnaesan-mcp` |
| image_tag | `latest` 또는 `main` |

> image_name에 `ghcr.io/` 포함하지 마세요.

---

## 4. GitHub Secrets (선택)

| Secret | 용도 |
|--------|------|
| `NAVER_CLIENT_ID` | 네이버 쇼핑 시장가 비교 |
| `NAVER_CLIENT_SECRET` | 네이버 쇼핑 시장가 비교 |

미설정 시 시장가 비교 툴은 안내 메시지 반환, 나머지 툴 정상 동작.

---

## 5. 성공 확인

Status **Active** 후:

```bash
curl -sS "https://nidonnaesan-mcp-server.playmcp-endpoint.kakaocloud.io/mcp" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-03-26","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}'
```

v1.1 스모크 테스트 프롬프트:
- `마감 하루 안 남은 협찬 5개 알려줘` → `get_urgent_campaigns`
- `서울쪽 레스토랑 협찬 추천해줘` → `search_campaigns_by_need`
- `체험단 선정률 올리는 방법` → `get_sponsorship_tips` (28개 팁)

카톡 예시 10개 → [PLAYMCP_EXAMPLES.md](PLAYMCP_EXAMPLES.md)

---

## 6. 로컬 실행

```bash
pip install -r requirements.txt
python scripts/sync_campaigns.py
python nidonnaesan_server.py
```

MCP Inspector: `http://localhost:8000/mcp`

---

## 7. 자주 하는 실수

| 실수 | 결과 |
|------|------|
| Private GHCR + PAT 없음 | Starting → Error |
| arm64 로컬 빌드 | KC는 linux/amd64만 (Actions 사용) |
| 툴명에 kakao 포함 | 심사 반려 |
