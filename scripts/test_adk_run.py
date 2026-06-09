"""Test ADK agent run with Gemini."""
import asyncio
import os
import uuid
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools.mcp_tool import McpToolset, StreamableHTTPConnectionParams
from google.genai import types


async def main() -> None:
    mcp = McpToolset(
        connection_params=StreamableHTTPConnectionParams(
            url=os.environ["ELASTIC_MCP_URL"],
            headers={"Authorization": f"ApiKey {os.environ['ELASTIC_API_KEY']}"},
        )
    )
    agent = Agent(
        name="alertsense",
        model=os.getenv("GEMINI_MODEL", "gemini-2.0-flash"),
        instruction=(
            "You are AlertSense. When asked about an incident, call search_error_logs "
            "then summarize findings in 2 sentences."
        ),
        tools=[mcp],
    )
    session_service = InMemorySessionService()
    runner = Runner(agent=agent, app_name="alertsense", session_service=session_service)
    session_id = str(uuid.uuid4())
    await session_service.create_session(app_name="alertsense", user_id="demo", session_id=session_id)

    msg = types.Content(
        role="user",
        parts=[types.Part(text="Customers say checkout is slow — what broke?")],
    )
    final = ""
    async for event in runner.run_async(user_id="demo", session_id=session_id, new_message=msg):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    final = part.text
                    print("EVENT:", part.text[:200])
    print("FINAL:", final[:400] if final else "(empty)")


if __name__ == "__main__":
    asyncio.run(main())
