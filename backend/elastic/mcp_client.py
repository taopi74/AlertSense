"""Elastic Agent Builder MCP client (Streamable HTTP)."""

from __future__ import annotations

import json
import logging
from typing import Any

import httpx

from backend.config import settings
from backend.models.schemas import LogHit

logger = logging.getLogger(__name__)

MCP_HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json, text/event-stream",
}


class ElasticMCPClient:
    """Minimal MCP client for Elastic Agent Builder tools."""

    def __init__(self) -> None:
        self._initialized = False

    async def search_error_logs(self, query: str, limit: int = 25) -> list[LogHit]:
        if not settings.elastic_mcp_configured:
            return []

        headers = {
            **MCP_HEADERS,
            "Authorization": f"ApiKey {settings.elastic_api_key}",
        }
        url = settings.elastic_mcp_url
        tool_name = settings.elastic_mcp_tool_name

        try:
            async with httpx.AsyncClient(timeout=45.0) as client:
                await self._initialize(client, url, headers)
                payload = {
                    "jsonrpc": "2.0",
                    "id": 3,
                    "method": "tools/call",
                    "params": {
                        "name": tool_name,
                        "arguments": {"query": query, "limit": limit},
                    },
                }
                response = await client.post(url, headers=headers, json=payload)
                response.raise_for_status()
                data = response.json()
                hits = self._parse_tool_result(data)
                logger.info("Elastic MCP (%s) returned %d hits", tool_name, len(hits))
                return hits
        except Exception as exc:
            logger.warning("Elastic MCP search failed: %s", exc)
            return []

    async def _initialize(self, client: httpx.AsyncClient, url: str, headers: dict[str, str]) -> None:
        if self._initialized:
            return
        init_payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "alertsense", "version": "1.0.0"},
            },
        }
        response = await client.post(url, headers=headers, json=init_payload)
        response.raise_for_status()
        self._initialized = True

    def _parse_tool_result(self, data: dict[str, Any]) -> list[LogHit]:
        hits: list[LogHit] = []
        content = data.get("result", {}).get("content", [])

        for item in content:
            text = item.get("text", "")
            if not text:
                if item.get("type") == "esql_results":
                    hits.extend(self._parse_esql_block(item.get("data", {})))
                continue
            try:
                parsed = json.loads(text)
                if isinstance(parsed, dict) and "results" in parsed:
                    for block in parsed["results"]:
                        if block.get("type") == "esql_results":
                            hits.extend(self._parse_esql_block(block.get("data", {})))
                elif isinstance(parsed, list):
                    for doc in parsed:
                        hits.append(self._doc_to_hit(doc))
                elif isinstance(parsed, dict):
                    for row in parsed.get("hits", parsed.get("documents", [])):
                        source = row.get("_source", row)
                        hits.append(self._doc_to_hit(source))
            except json.JSONDecodeError:
                if item.get("type") == "esql_results":
                    hits.extend(self._parse_esql_block(item.get("data", {})))

        return hits

    def _parse_esql_block(self, data: dict[str, Any]) -> list[LogHit]:
        columns = [c.get("name", "") for c in data.get("columns", [])]
        values = data.get("values", [])
        hits: list[LogHit] = []

        for row in values:
            doc = dict(zip(columns, row, strict=False))
            # Prefer non-.keyword fields
            clean = {}
            for key, val in doc.items():
                if key.endswith(".keyword"):
                    base = key[:-8]
                    if base not in doc:
                        clean[base] = val
                elif key not in clean:
                    clean[key] = val
            hits.append(self._doc_to_hit(clean))

        return hits

    def _doc_to_hit(self, doc: dict[str, Any]) -> LogHit:
        return LogHit(
            timestamp=str(doc.get("timestamp", doc.get("@timestamp", ""))),
            service=str(doc.get("service", doc.get("service.name", "unknown"))),
            level=str(doc.get("level", doc.get("log.level", "INFO"))),
            message=str(doc.get("message", doc.get("log.message", ""))),
            trace_id=doc.get("trace_id") or doc.get("trace.id"),
        )


mcp_client = ElasticMCPClient()
