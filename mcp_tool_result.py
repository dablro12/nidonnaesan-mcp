"""MCP Tool 응답 — isError 패턴."""

from __future__ import annotations

import functools
import inspect
from collections.abc import Callable
from typing import Any

from mcp.server.fastmcp import FastMCP
from mcp.types import CallToolResult, TextContent

FAILURE_MARKERS = ("서비스 오류:", "Unknown tip topic", "지원하지 않는")


def tool_error(message: str) -> CallToolResult:
    body = message if message.startswith("서비스 오류:") else f"서비스 오류: {message}"
    return CallToolResult(
        content=[TextContent(type="text", text=body)],
        isError=True,
    )


def _wrap_tool_fn(name: str, fn: Callable[..., Any]) -> Callable[..., Any]:
    if inspect.iscoroutinefunction(fn):

        @functools.wraps(fn)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return await fn(*args, **kwargs)
            except ValueError as exc:
                return tool_error(str(exc))
            except Exception as exc:  # noqa: BLE001
                return tool_error(f"{exc.__class__.__name__}: {exc}")

        return async_wrapper

    @functools.wraps(fn)
    def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return fn(*args, **kwargs)
        except ValueError as exc:
            return tool_error(str(exc))
        except Exception as exc:  # noqa: BLE001
            return tool_error(f"{exc.__class__.__name__}: {exc}")

    return sync_wrapper


def install_tool_error_wrapping(mcp: FastMCP) -> None:
    for tool in mcp._tool_manager.list_tools():  # noqa: SLF001
        tool.fn = _wrap_tool_fn(tool.name, tool.fn)
