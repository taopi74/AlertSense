"""Quick ADK + MCP smoke test."""
import asyncio
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

from google.adk.agents import Agent
from google.adk.tools.mcp_tool import MCPToolset, StreamableHTTPConnectionParams


async def main() -> None:
    mcp = MCPToolset(
        connection_params=StreamableHTTPConnectionParams(
            url=os.environ["ELASTIC_MCP_URL"],
            headers={"Authorization": f"ApiKey {os.environ['ELASTIC_API_KEY']}"},
        )
    )
    agent = Agent(
        name="alertsense",
        model=os.getenv("GEMINI_MODEL", "gemini-2.0-flash"),
        instruction="You are AlertSense incident triage agent.",
        tools=[mcp],
    )
    print("Agent created:", agent.name)
    tools = await mcp.get_tools()
    print("MCP tools:", [t.name for t in tools[:5]], "...")


if __name__ == "__main__":
    asyncio.run(main())
