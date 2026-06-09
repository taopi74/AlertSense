"""Google ADK import compatibility across package versions."""

from __future__ import annotations

from typing import Any


def load_adk_mcp() -> tuple[Any, Any, Any, Any, Any, Any]:
    """Return ADK classes, supporting both old (MCPToolset) and new (McpToolset) APIs."""
    from google.adk.agents import Agent
    from google.adk.runners import Runner
    from google.adk.sessions import InMemorySessionService
    from google.genai import types

    try:
        from google.adk.tools.mcp_tool import McpToolset as McpToolsetCls
    except ImportError:
        from google.adk.tools.mcp_tool import MCPToolset as McpToolsetCls

    try:
        from google.adk.tools.mcp_tool import StreamableHTTPConnectionParams
    except ImportError:
        try:
            from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams
        except ImportError:
            from google.adk.tools.mcp_tool.mcp_session_manager import (
                StreamableHTTPServerParams as StreamableHTTPConnectionParams,
            )

    return Agent, Runner, InMemorySessionService, types, McpToolsetCls, StreamableHTTPConnectionParams


def check_adk_available() -> tuple[bool, str | None]:
    try:
        import google.adk  # noqa: F401 — ensure package loads on Vercel
        load_adk_mcp()
        return True, None
    except Exception as exc:
        return False, f"{type(exc).__name__}: {exc}"
