"""PlayMCP tools/list description 필수 검증."""

import asyncio

from nidonnaesan_server import mcp

EXPECTED = {
    "get_campaign_recommendations",
    "get_today_hot_campaigns",
    "search_campaigns_by_need",
    "get_urgent_campaigns",
    "compare_product_market_price",
    "analyze_channel_profile",
    "generate_application_comment",
    "get_campaign_link",
    "run_sponsorship_aptitude_test",
    "get_sponsorship_tips",
    "set_reviewer_profile",
    "get_reviewer_profile",
}


def test_all_tools_have_description() -> None:
    async def _run() -> None:
        tools = await mcp.list_tools()
        names = {t.name for t in tools}
        assert names == EXPECTED
        for t in tools:
            assert t.description and t.description.strip(), f"missing description: {t.name}"
            assert "OUTPUT RULE" not in t.description, t.name
            assert "USE FIRST" not in t.description, t.name
            assert len(t.description) < 200, t.name

    asyncio.run(_run())
