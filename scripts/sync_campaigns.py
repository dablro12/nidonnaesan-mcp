#!/usr/bin/env python3
"""체험단 API 전체 캠페인 동기화 → data/campaigns/campaigns.json"""

from __future__ import annotations

import asyncio
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import httpx

API_BASE = os.getenv("CAMPAIGN_API_BASE", "https://api-on7fpupona-du.a.run.app")
OUT_DIR = Path(__file__).resolve().parents[1] / "data" / "campaigns"
OUT_FILE = OUT_DIR / "campaigns.json"
PAGE_SIZE = 500


async def sync_all() -> dict:
    campaigns: list[dict] = []
    total = 0
    updated_at = None

    async with httpx.AsyncClient(timeout=30.0) as client:
        offset = 0
        while True:
            resp = await client.get(
                f"{API_BASE}/campaigns",
                params={"limit": PAGE_SIZE, "offset": offset},
            )
            resp.raise_for_status()
            data = resp.json()
            batch = data.get("campaigns") or []
            total = int(data.get("total") or 0)
            updated_at = data.get("updatedAt")
            if not batch:
                break
            campaigns.extend(batch)
            print(f"  fetched {len(campaigns)}/{total} (offset={offset})", flush=True)
            if len(batch) < PAGE_SIZE or len(campaigns) >= total:
                break
            offset += PAGE_SIZE

    payload = {
        "total": len(campaigns),
        "api_total": total,
        "updatedAt": updated_at,
        "synced_at": datetime.now(timezone.utc).isoformat(),
        "campaigns": campaigns,
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_FILE.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    return payload


def main() -> None:
    print(f"Syncing campaigns from {API_BASE} ...")
    payload = asyncio.run(sync_all())
    print(f"Done: {payload['total']} campaigns → {OUT_FILE}")


if __name__ == "__main__":
    main()
