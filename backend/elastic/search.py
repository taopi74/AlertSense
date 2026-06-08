"""Elastic search integration — MCP client and direct Elasticsearch fallback."""

from __future__ import annotations

import json
import logging
from typing import Any

import httpx

from backend.config import settings
from backend.elastic.mock_data import search_mock_logs
from backend.models.schemas import LogHit

logger = logging.getLogger(__name__)


class ElasticSearchService:
    """Search logs via Elastic MCP, direct ES API, or demo mock data."""

    async def search_logs(self, query: str, time_window_hours: int = 24, limit: int = 25) -> tuple[list[LogHit], str]:
        if settings.use_demo:
            hits = self._from_mock(query, limit)
            return hits, "demo"

        # Direct ES first — most reliable for our logs-alertsense index
        if settings.elasticsearch_configured:
            hits = await self._search_via_es(query, time_window_hours, limit)
            if hits:
                return hits, "elasticsearch"

        if settings.elastic_mcp_configured:
            hits = await self._search_via_mcp(query, time_window_hours, limit)
            if hits:
                return hits, "elastic_mcp"

        hits = self._from_mock(query, limit)
        return hits, "demo_fallback"

    def _from_mock(self, query: str, limit: int) -> list[LogHit]:
        raw = search_mock_logs(query, limit=limit)
        return [self._to_log_hit(r) for r in raw]

    def _to_log_hit(self, doc: dict[str, Any]) -> LogHit:
        return LogHit(
            timestamp=str(doc.get("timestamp", doc.get("@timestamp", ""))),
            service=str(doc.get("service", doc.get("service.name", "unknown"))),
            level=str(doc.get("level", doc.get("log.level", "INFO"))),
            message=str(doc.get("message", doc.get("log.message", ""))),
            trace_id=doc.get("trace_id") or doc.get("trace.id"),
        )

    async def _search_via_mcp(self, query: str, time_window_hours: int, limit: int) -> list[LogHit]:
        """Call Elastic Agent Builder MCP endpoint (streamable HTTP)."""
        search_query = (
            f"{query} level:(ERROR OR WARN) "
            f"AND @timestamp:[now-{time_window_hours}h TO now]"
        )

        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "search",
                "arguments": {
                    "query": search_query,
                    "size": limit,
                },
            },
        }

        headers = {
            "Authorization": f"ApiKey {settings.elastic_api_key}",
            "Content-Type": "application/json",
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    settings.elastic_mcp_url,
                    headers=headers,
                    json=payload,
                )
                response.raise_for_status()
                data = response.json()
                return self._parse_mcp_results(data)
        except Exception as exc:
            logger.warning("Elastic MCP search failed: %s", exc)
            return []

    def _parse_mcp_results(self, data: dict[str, Any]) -> list[LogHit]:
        hits: list[LogHit] = []
        result = data.get("result", {})
        content = result.get("content", [])

        for item in content:
            text = item.get("text", "")
            if not text:
                continue
            try:
                parsed = json.loads(text)
                if isinstance(parsed, list):
                    for doc in parsed:
                        hits.append(self._to_log_hit(doc))
                elif isinstance(parsed, dict):
                    for hit in parsed.get("hits", parsed.get("documents", [])):
                        source = hit.get("_source", hit)
                        hits.append(self._to_log_hit(source))
            except json.JSONDecodeError:
                hits.append(
                    LogHit(
                        timestamp="",
                        service="elastic",
                        level="INFO",
                        message=text[:500],
                    )
                )
        return hits

    async def _search_via_es(self, query: str, time_window_hours: int, limit: int) -> list[LogHit]:
        """Direct Elasticsearch query against logs-alertsense index."""
        keywords = [w for w in query.lower().split() if len(w) > 2]
        should_clauses: list[dict[str, Any]] = [
            {"multi_match": {"query": query, "fields": ["message", "service", "level"]}},
        ]
        for kw in keywords[:6]:
            should_clauses.append({"wildcard": {"message": {"value": f"*{kw}*"}}})
            should_clauses.append({"term": {"service": kw}})

        es_query = {
            "size": limit,
            "sort": [{"timestamp": {"order": "desc", "unmapped_type": "date"}}],
            "query": {
                "bool": {
                    "must": [
                        {"query_string": {"query": "level:(ERROR OR WARN)"}},
                    ],
                    "should": should_clauses,
                    "minimum_should_match": 1,
                }
            },
        }

        headers = {
            "Authorization": f"ApiKey {settings.elasticsearch_api_key}",
            "Content-Type": "application/json",
        }

        url = f"{settings.elasticsearch_url.rstrip('/')}/logs-alertsense/_search"

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, headers=headers, json=es_query)
                response.raise_for_status()
                data = response.json()
                hits = []
                for hit in data.get("hits", {}).get("hits", []):
                    hits.append(self._to_log_hit(hit.get("_source", {})))
                logger.info("Elasticsearch returned %d hits", len(hits))
                return hits
        except Exception as exc:
            logger.warning("Elasticsearch search failed: %s", exc)
            return []


elastic_service = ElasticSearchService()
