"""체험단 캠페인 API 클라이언트 + 로컬 data/campaigns 캐시."""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any

import httpx

from runtime_paths import data_path

CAMPAIGN_API_BASE = os.getenv(
    "CAMPAIGN_API_BASE",
    "https://api-on7fpupona-du.a.run.app",
)
CAMPAIGN_DATA_FILE = Path(
    os.getenv("CAMPAIGN_DATA_FILE", str(data_path("campaigns", "campaigns.json")))
)
_CACHE_TTL_SEC = int(os.getenv("CAMPAIGN_CACHE_TTL_SEC", "900"))
_PAGE_SIZE = 500

_store: dict[str, Any] = {
    "campaigns": [],
    "by_id": {},
    "fetched_at": 0.0,
    "meta": {},
}


def _build_index(campaigns: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {str(c["id"]): c for c in campaigns if c.get("id")}


def _load_from_disk() -> bool:
    if not CAMPAIGN_DATA_FILE.exists():
        return False
    try:
        payload = json.loads(CAMPAIGN_DATA_FILE.read_text(encoding="utf-8"))
        campaigns = payload.get("campaigns") or []
        if not campaigns:
            return False
        _store["campaigns"] = campaigns
        _store["by_id"] = _build_index(campaigns)
        _store["meta"] = {
            "total": payload.get("total"),
            "api_total": payload.get("api_total"),
            "synced_at": payload.get("synced_at"),
            "updatedAt": payload.get("updatedAt"),
        }
        _store["fetched_at"] = time.monotonic()
        return True
    except (json.JSONDecodeError, OSError):
        return False


async def _fetch_all_from_api() -> list[dict[str, Any]]:
    campaigns: list[dict[str, Any]] = []
    total = 0
    offset = 0

    async with httpx.AsyncClient(timeout=30.0) as client:
        while True:
            resp = await client.get(
                f"{CAMPAIGN_API_BASE}/campaigns",
                params={"limit": _PAGE_SIZE, "offset": offset},
            )
            resp.raise_for_status()
            data = resp.json()
            batch = data.get("campaigns") or []
            total = int(data.get("total") or 0)
            if not batch:
                break
            campaigns.extend(batch)
            if len(batch) < _PAGE_SIZE or len(campaigns) >= total:
                break
            offset += _PAGE_SIZE

    return campaigns


async def _persist_to_disk(campaigns: list[dict[str, Any]], *, api_total: int | None = None) -> None:
    from datetime import datetime, timezone

    CAMPAIGN_DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "total": len(campaigns),
        "api_total": api_total or len(campaigns),
        "synced_at": datetime.now(timezone.utc).isoformat(),
        "campaigns": campaigns,
    }
    CAMPAIGN_DATA_FILE.write_text(
        json.dumps(payload, ensure_ascii=False),
        encoding="utf-8",
    )


def _set_store(campaigns: list[dict[str, Any]], *, api_total: int | None = None) -> list[dict[str, Any]]:
    _store["campaigns"] = campaigns
    _store["by_id"] = _build_index(campaigns)
    _store["fetched_at"] = time.monotonic()
    _store["meta"] = {"total": len(campaigns), "api_total": api_total or len(campaigns)}
    return campaigns


async def fetch_all_campaigns(*, force: bool = False) -> list[dict[str, Any]]:
    now = time.monotonic()
    if (
        not force
        and _store["campaigns"]
        and now - _store["fetched_at"] < _CACHE_TTL_SEC
    ):
        return _store["campaigns"]

    if not force and not _store["campaigns"]:
        if _load_from_disk():
            return _store["campaigns"]

    campaigns = await _fetch_all_from_api()
    _set_store(campaigns, api_total=len(campaigns))
    await _persist_to_disk(campaigns, api_total=len(campaigns))
    return campaigns


def get_campaign_by_id(campaign_id: str) -> dict[str, Any] | None:
    if not _store["by_id"] and CAMPAIGN_DATA_FILE.exists():
        _load_from_disk()
    return _store["by_id"].get(campaign_id)


def _numeric_suffix(campaign_id: str) -> str | None:
    import re

    cid = (campaign_id or "").strip()
    if not cid:
        return None
    if cid.isdigit():
        return cid.lstrip("0") or "0"
    m = re.search(r"(\d{4,})$", cid.replace("CMPN_", "").replace("cmpn_", ""))
    if m:
        return m.group(1).lstrip("0") or "0"
    return None


def _find_by_suffix(suffix: str) -> dict[str, Any] | None:
    for campaign in _store.get("campaigns") or []:
        cid = str(campaign.get("id") or "")
        if cid.endswith(f"-{suffix}") or cid.split("-")[-1] == suffix:
            return campaign
    return None


async def resolve_campaign_id(campaign_id: str) -> dict[str, Any] | None:
    """revu-1367756 / 1367756 / CMPN_0000001367756 등 해석."""
    cid = (campaign_id or "").strip()
    if not cid:
        return None

    local = get_campaign_by_id(cid)
    if local:
        return local

    if not _store["campaigns"]:
        await fetch_all_campaigns()

    local = get_campaign_by_id(cid)
    if local:
        return local

    suffix = _numeric_suffix(cid)
    if suffix:
        found = _find_by_suffix(suffix)
        if found:
            return found

    async with httpx.AsyncClient(timeout=10.0) as client:
        for path_id in (cid, f"revu-{suffix}" if suffix else None):
            if not path_id:
                continue
            resp = await client.get(f"{CAMPAIGN_API_BASE}/campaigns/{path_id}")
            if resp.status_code == 404:
                continue
            resp.raise_for_status()
            data = resp.json()
            campaign = data.get("campaign") if isinstance(data, dict) and "campaign" in data else data
            if isinstance(campaign, dict) and campaign.get("id"):
                _store["by_id"][str(campaign["id"])] = campaign
                return campaign
    return None


async def fetch_campaign_by_id(campaign_id: str) -> dict[str, Any] | None:
    return await resolve_campaign_id(campaign_id)


def get_campaign_meta() -> dict[str, Any]:
    if not _store["meta"] and CAMPAIGN_DATA_FILE.exists():
        _load_from_disk()
    return dict(_store.get("meta") or {})


def clear_campaign_cache() -> None:
    _store["campaigns"] = []
    _store["by_id"] = {}
    _store["fetched_at"] = 0.0
    _store["meta"] = {}
