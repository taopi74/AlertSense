#!/usr/bin/env python3
"""Seed sample checkout-incident logs into Elasticsearch."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

try:
    from dotenv import load_dotenv
    from elasticsearch import Elasticsearch, helpers
except ImportError:
    print("Install dependencies: pip install elasticsearch python-dotenv")
    sys.exit(1)

INDEX = "logs-alertsense"
DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "sample_logs.ndjson"
ROOT = Path(__file__).resolve().parent.parent


def _resolve_es_url(mcp_url: str) -> str:
    """Derive Elasticsearch URL from Kibana MCP URL when not set explicitly."""
    if ".kb." in mcp_url:
        return mcp_url.split("/api/")[0].replace(".kb.", ".es.") + ":443"
    return ""


def main() -> None:
    load_dotenv(ROOT / ".env")

    url = os.getenv("ELASTICSEARCH_URL", "")
    api_key = os.getenv("ELASTICSEARCH_API_KEY", "") or os.getenv("ELASTIC_API_KEY", "")

    if not url:
        url = _resolve_es_url(os.getenv("ELASTIC_MCP_URL", ""))

    if not url or not api_key:
        print("Set ELASTICSEARCH_URL + ELASTICSEARCH_API_KEY in .env")
        print("Or set ELASTIC_MCP_URL + ELASTIC_API_KEY (URL is auto-derived)")
        sys.exit(1)

    client = Elasticsearch(url, api_key=api_key)

    if not client.ping():
        print("Cannot connect to Elasticsearch")
        sys.exit(1)

    actions = []
    with DATA_FILE.open(encoding="utf-8") as f:
        for i, line in enumerate(f):
            doc = json.loads(line)
            actions.append({"_index": INDEX, "_id": i + 1, "_source": doc})

    helpers.bulk(client, actions)
    client.indices.refresh(index=INDEX)
    print(f"Seeded {len(actions)} documents into index '{INDEX}'")


if __name__ == "__main__":
    main()
