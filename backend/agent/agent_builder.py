"""Google Cloud Agent Builder integration via ADK."""

from __future__ import annotations

import asyncio
import logging
import uuid
from typing import Any

from backend.config import settings

logger = logging.getLogger(__name__)


class AgentBuilderService:
    """Runs Google ADK agent with Gemini + Elastic MCP (hackathon requirement)."""

    def __init__(self) -> None:
        self._available = False
        self.import_error = None
        try:
            from google.adk.agents import Agent  # noqa: F401
            from google.adk.tools.mcp_tool import McpToolset  # noqa: F401

            self._available = True
        except Exception as exc:
            self.import_error = f"{type(exc).__name__}: {str(exc)}"
            logger.warning("google-adk import failed: %s", exc)

    @property
    def configured(self) -> bool:
        return (
            self._available
            and settings.gemini_configured
            and settings.elastic_mcp_configured
        )

    async def analyze_incident(self, query: str, log_summary: str) -> str | None:
        """Invoke ADK agent (Gemini + Elastic MCP tools) for incident analysis."""
        if not self.configured:
            return None

        try:
            return await asyncio.wait_for(
                self._run_adk_analysis(query, log_summary),
                timeout=45.0,
            )
        except asyncio.TimeoutError:
            logger.warning("Agent Builder (ADK) timed out after 45s")
            return None
        except Exception as exc:
            logger.warning("Agent Builder (ADK) failed: %s", exc)
            return None

    async def _run_adk_analysis(self, query: str, log_summary: str) -> str | None:
        try:
            from google.adk.agents import Agent
            from google.adk.runners import Runner
            from google.adk.sessions import InMemorySessionService
            from google.adk.tools.mcp_tool import McpToolset, StreamableHTTPConnectionParams
            from google.genai import types

            mcp = McpToolset(
                connection_params=StreamableHTTPConnectionParams(
                    url=settings.elastic_mcp_url,
                    headers={"Authorization": f"ApiKey {settings.elastic_api_key}"},
                )
            )
            agent = Agent(
                name="alertsense",
                model=settings.gemini_model,
                instruction=(
                    "You are AlertSense, an incident triage agent on Google Cloud Agent Builder. "
                    "Use the search_error_logs tool to verify log evidence, then explain root cause "
                    "in 3-5 sentences. Be specific about services and errors."
                ),
                tools=[mcp],
            )

            session_service = InMemorySessionService()
            runner = Runner(agent=agent, app_name="alertsense", session_service=session_service)
            session_id = str(uuid.uuid4())
            await session_service.create_session(
                app_name="alertsense",
                user_id="alertsense",
                session_id=session_id,
            )

            prompt = (
                f"Incident: {query}\n\n"
                f"Preliminary log summary:\n{log_summary}\n\n"
                "Call search_error_logs, then summarize root cause and impact."
            )
            message = types.Content(role="user", parts=[types.Part(text=prompt)])

            final_text = ""
            async for event in runner.run_async(
                user_id="alertsense",
                session_id=session_id,
                new_message=message,
            ):
                if event.content and event.content.parts:
                    for part in event.content.parts:
                        if part.text:
                            final_text = part.text

            if final_text:
                logger.info("Agent Builder (ADK) analysis complete (%d chars)", len(final_text))
            return final_text.strip() or None

        except Exception as exc:
            logger.warning("Agent Builder (ADK) inner failed: %s", exc)
            return None

    async def health_check(self) -> dict[str, Any]:
        if not self.configured:
            return {"status": "disabled", "reason": "missing adk, gemini, or elastic mcp"}
        return {"status": "ok", "framework": "google-adk", "model": settings.gemini_model}


agent_builder_service = AgentBuilderService()
