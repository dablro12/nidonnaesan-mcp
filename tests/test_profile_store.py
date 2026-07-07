import os
import tempfile
from pathlib import Path

import profile_store


def test_set_and_get_profile(monkeypatch, tmp_path):
    db = tmp_path / "test.db"
    monkeypatch.setattr(profile_store, "DB_PATH", db)
    saved = profile_store.set_profile(
        {"aptitude_type": "food_explorer", "preferred_category": "맛집"},
        profile_fallback={"_user_key": "test:user1"},
    )
    assert saved["aptitude_type"] == "food_explorer"
    loaded = profile_store.get_profile(profile_fallback={"_user_key": "test:user1"})
    assert loaded["preferred_category"] == "맛집"


def test_read_tip_ids_append(monkeypatch, tmp_path):
    db = tmp_path / "test2.db"
    monkeypatch.setattr(profile_store, "DB_PATH", db)
    profile_store.set_profile(
        {"read_tip_ids": ["selection_rate"]},
        profile_fallback={"_user_key": "test:user2"},
    )
    saved = profile_store.set_profile(
        {"read_tip_ids": ["platform"]},
        profile_fallback={"_user_key": "test:user2"},
    )
    assert "selection_rate" in saved["read_tip_ids"]
    assert "platform" in saved["read_tip_ids"]
