"""campaign_id 숫자·CMPN 접두 해석 테스트."""

import pytest

from campaign_client import _find_by_suffix, _numeric_suffix, resolve_campaign_id


def test_numeric_suffix() -> None:
    assert _numeric_suffix("revu-1367756") == "1367756"
    assert _numeric_suffix("1367756") == "1367756"
    assert _numeric_suffix("CMPN_0000001367756") == "1367756"


@pytest.mark.asyncio
async def test_resolve_campaign_id_by_suffix() -> None:
    from campaign_client import _set_store

    _set_store([{"id": "revu-1367756", "title": "test"}])
    c = await resolve_campaign_id("1367756")
    assert c is not None
    assert str(c["id"]).endswith("1367756")


def test_find_by_suffix() -> None:
    from campaign_client import _set_store

    _set_store(
        [
            {"id": "revu-999", "title": "t"},
            {"id": "gangnam-888", "title": "t2"},
        ]
    )
    assert _find_by_suffix("999")["id"] == "revu-999"
