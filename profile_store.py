"""리뷰어 프로필 SQLite 저장소 (Stateless + set_profile 패턴)."""

from __future__ import annotations

import json
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DB_PATH = Path(os.getenv("PROFILE_DB_PATH", "data/profiles.db"))

DEFAULT_PROFILE: dict[str, Any] = {
    "channel_url": None,
    "aptitude_type": None,
    "preferred_media": None,
    "preferred_category": None,
    "preferred_type": None,
    "region": None,
    "experience_level": "none",
    "read_tip_ids": [],
}


def _conn() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS reviewer_profiles (
            user_key TEXT PRIMARY KEY,
            profile_json TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """
    )
    return conn


def _user_key(oauth_sub: str | None, profile_fallback: dict[str, Any] | None) -> str:
    if oauth_sub:
        return f"oauth:{oauth_sub}"
    if profile_fallback and profile_fallback.get("_user_key"):
        return str(profile_fallback["_user_key"])
    return "anonymous:default"


def _merge_profile(existing: dict[str, Any], updates: dict[str, Any]) -> dict[str, Any]:
    merged = {**DEFAULT_PROFILE, **existing}
    for key, val in updates.items():
        if key == "read_tip_ids" and isinstance(val, list):
            current = list(merged.get("read_tip_ids") or [])
            for tip_id in val:
                if tip_id not in current:
                    current.append(tip_id)
            merged["read_tip_ids"] = current
        elif val is not None:
            merged[key] = val
    merged["updated_at"] = datetime.now(timezone.utc).isoformat()
    return merged


def get_profile(
    *,
    oauth_sub: str | None = None,
    profile_fallback: dict[str, Any] | None = None,
) -> dict[str, Any] | None:
    key = _user_key(oauth_sub, profile_fallback)
    with _conn() as conn:
        row = conn.execute(
            "SELECT profile_json FROM reviewer_profiles WHERE user_key = ?",
            (key,),
        ).fetchone()
    if row:
        return json.loads(row["profile_json"])

    if profile_fallback and not oauth_sub:
        has_data = any(profile_fallback.get(k) for k in DEFAULT_PROFILE if k != "read_tip_ids")
        if has_data or profile_fallback.get("read_tip_ids"):
            return _merge_profile({}, profile_fallback)
    return None


def set_profile(
    updates: dict[str, Any],
    *,
    oauth_sub: str | None = None,
    profile_fallback: dict[str, Any] | None = None,
) -> dict[str, Any]:
    key = _user_key(oauth_sub, profile_fallback)
    existing = get_profile(oauth_sub=oauth_sub, profile_fallback=profile_fallback) or {}
    merged = _merge_profile(existing, updates)
    merged.pop("_user_key", None)

    with _conn() as conn:
        conn.execute(
            """
            INSERT INTO reviewer_profiles (user_key, profile_json, updated_at)
            VALUES (?, ?, ?)
            ON CONFLICT(user_key) DO UPDATE SET
                profile_json = excluded.profile_json,
                updated_at = excluded.updated_at
            """,
            (key, json.dumps(merged, ensure_ascii=False), merged["updated_at"]),
        )
        conn.commit()
    return merged


def filter_defaults(profile: dict[str, Any] | None) -> dict[str, str]:
    if not profile:
        return {}
    defaults: dict[str, str] = {}
    mapping = {
        "preferred_category": "category",
        "preferred_media": "mediaType",
        "preferred_type": "type",
    }
    for src, dst in mapping.items():
        val = profile.get(src)
        if val and val != "전체":
            defaults[dst] = val
    region = profile.get("region")
    if region and region not in ("전국", "전체"):
        defaults["region"] = region
    return defaults
