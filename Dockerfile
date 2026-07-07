# PlayMCP in KC — linux/amd64 빌드 필수
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY nidonnaesan_server.py ./
COPY src/ ./src/
COPY scripts/ ./scripts/
COPY data/ ./data/

RUN pip install --no-cache-dir httpx && python scripts/sync_campaigns.py && \
    python scripts/sync_blogreviewzip_tips.py && \
    test -f data/campaigns/campaigns.json

ARG NAVER_CLIENT_ID=""
ARG NAVER_CLIENT_SECRET=""
ARG CAMPAIGN_API_BASE="https://api-on7fpupona-du.a.run.app"
ARG PUBLIC_BASE_URL="https://nidonnaesan-mcp.playmcp-endpoint.kakaocloud.io"

ENV NAVER_CLIENT_ID=${NAVER_CLIENT_ID}
ENV NAVER_CLIENT_SECRET=${NAVER_CLIENT_SECRET}
ENV CAMPAIGN_API_BASE=${CAMPAIGN_API_BASE}
ENV PUBLIC_BASE_URL=${PUBLIC_BASE_URL}
ENV PROFILE_DB_PATH=/app/data/profiles.db

ENV MCP_HOST=0.0.0.0
ENV MCP_PORT=8000

EXPOSE 8000

CMD ["python", "nidonnaesan_server.py"]
