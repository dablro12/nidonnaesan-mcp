"""캠페인 데이터 백그라운드 동기화 — 시작 즉시 + 15분 주기."""

from __future__ import annotations

import asyncio
import logging
import os
import threading

from campaign_client import fetch_all_campaigns

logger = logging.getLogger(__name__)

SYNC_INTERVAL_SEC = int(os.getenv("CAMPAIGN_SYNC_INTERVAL_SEC", "900"))


async def sync_campaigns_once() -> int:
    campaigns = await fetch_all_campaigns(force=True)
    logger.info("campaign sync complete: %s campaigns", len(campaigns))
    return len(campaigns)


async def _sync_loop() -> None:
    while True:
        try:
            await sync_campaigns_once()
        except Exception as exc:
            logger.exception("campaign sync failed: %s", exc)
        await asyncio.sleep(SYNC_INTERVAL_SEC)


def start_background_sync() -> None:
    """데몬 스레드에서 즉시 1회 동기화 후 15분마다 반복."""

    def runner() -> None:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(sync_campaigns_once())
            loop.run_until_complete(_sync_loop())
        finally:
            loop.close()

    thread = threading.Thread(target=runner, name="campaign-sync", daemon=True)
    thread.start()
    logger.info("campaign background sync started (interval=%ss)", SYNC_INTERVAL_SEC)
