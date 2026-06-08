#!/usr/bin/env python3
"""Push a fresh live incident batch to Elasticsearch with current timestamps."""

from __future__ import annotations

import os
import sys
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

try:
    from dotenv import load_dotenv
    from elasticsearch import Elasticsearch, helpers
except ImportError:
    print("pip install elasticsearch python-dotenv")
    sys.exit(1)

ROOT = Path(__file__).resolve().parent.parent
INDEX = "logs-alertsense"


def _ts(minutes_ago: int) -> str:
    return (datetime.now(timezone.utc) - timedelta(minutes=minutes_ago)).isoformat()


def build_live_logs() -> list[dict]:
    trace = f"tr_live_{uuid.uuid4().hex[:8]}"
    return [
        {"timestamp": _ts(45), "service": "payment-api", "level": "WARN", "message": "Stripe latency p99=3800ms threshold=2000ms", "trace_id": trace},
        {"timestamp": _ts(30), "service": "payment-api", "level": "ERROR", "message": "Timeout calling stripe-api: Read timed out after 30s", "trace_id": trace},
        {"timestamp": _ts(28), "service": "checkout-api", "level": "ERROR", "message": "Payment failed reason=upstream_timeout session_id=chk_live_001", "trace_id": trace},
        {"timestamp": _ts(25), "service": "checkout-api", "level": "ERROR", "message": "Payment failed reason=upstream_timeout session_id=chk_live_002", "trace_id": trace},
        {"timestamp": _ts(22), "service": "frontend", "level": "ERROR", "message": "User reported slow checkout cart_abandon cart_id=c_live_99", "trace_id": trace},
        {"timestamp": _ts(20), "service": "payment-api", "level": "ERROR", "message": "Circuit breaker OPEN for stripe-api failures=8 window=5m", "trace_id": trace},
        {"timestamp": _ts(15), "service": "payment-api", "level": "ERROR", "message": "stripe-api connection pool exhausted max=50 active=50", "trace_id": trace},
        {"timestamp": _ts(10), "service": "checkout-api", "level": "WARN", "message": "Checkout completion rate dropped 28% vs baseline", "trace_id": trace},
        {"timestamp": _ts(40), "service": "deploy-bot", "level": "INFO", "message": "Deployed payment-api v2.14.0 to production", "trace_id": f"tr_dep_{uuid.uuid4().hex[:6]}"},
    ]


def main() -> None:
    load_dotenv(ROOT / ".env")
    url = os.getenv("ELASTICSEARCH_URL", "")
    api_key = os.getenv("ELASTICSEARCH_API_KEY", "") or os.getenv("ELASTIC_API_KEY", "")

    if not url or not api_key:
        print("Set ELASTICSEARCH_URL and ELASTICSEARCH_API_KEY in .env")
        sys.exit(1)

    client = Elasticsearch(url, api_key=api_key)
    logs = build_live_logs()
    actions = [{"_index": INDEX, "_source": doc} for doc in logs]
    helpers.bulk(client, actions)
    client.indices.refresh(index=INDEX)
    print(f"Injected {len(logs)} LIVE logs into '{INDEX}' at {datetime.now(timezone.utc).isoformat()}")


if __name__ == "__main__":
    main()
