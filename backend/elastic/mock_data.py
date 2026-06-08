"""Mock application logs for demo mode (checkout incident scenario)."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

NOW = datetime.now(timezone.utc)


def _ts(minutes_ago: int) -> str:
    return (NOW - timedelta(minutes=minutes_ago)).isoformat()


MOCK_LOGS: list[dict] = [
    {
        "timestamp": _ts(180),
        "service": "checkout-api",
        "level": "INFO",
        "message": "Checkout session started session_id=chk_8842",
        "trace_id": "tr_a001",
    },
    {
        "timestamp": _ts(120),
        "service": "payment-api",
        "level": "WARN",
        "message": "Payment gateway latency p99=4200ms threshold=2000ms",
        "trace_id": "tr_b002",
    },
    {
        "timestamp": _ts(95),
        "service": "payment-api",
        "level": "ERROR",
        "message": "Timeout calling stripe-api: Read timed out after 30s",
        "trace_id": "tr_b003",
    },
    {
        "timestamp": _ts(90),
        "service": "checkout-api",
        "level": "ERROR",
        "message": "Payment failed for session_id=chk_8842 reason=upstream_timeout",
        "trace_id": "tr_b003",
    },
    {
        "timestamp": _ts(88),
        "service": "checkout-api",
        "level": "ERROR",
        "message": "Payment failed for session_id=chk_9103 reason=upstream_timeout",
        "trace_id": "tr_b004",
    },
    {
        "timestamp": _ts(85),
        "service": "checkout-api",
        "level": "ERROR",
        "message": "Payment failed for session_id=chk_9107 reason=upstream_timeout",
        "trace_id": "tr_b005",
    },
    {
        "timestamp": _ts(82),
        "service": "frontend",
        "level": "ERROR",
        "message": "User reported slow checkout - cart_abandon event cart_id=c_4421",
        "trace_id": "tr_c006",
    },
    {
        "timestamp": _ts(80),
        "service": "payment-api",
        "level": "ERROR",
        "message": "Circuit breaker OPEN for stripe-api failures=12 window=5m",
        "trace_id": "tr_b007",
    },
    {
        "timestamp": _ts(75),
        "service": "deploy-bot",
        "level": "INFO",
        "message": "Deployed payment-api v2.14.0 to production 95 minutes ago",
        "trace_id": "tr_d008",
    },
    {
        "timestamp": _ts(70),
        "service": "payment-api",
        "level": "ERROR",
        "message": "stripe-api connection pool exhausted max=50 active=50",
        "trace_id": "tr_b009",
    },
    {
        "timestamp": _ts(60),
        "service": "checkout-api",
        "level": "WARN",
        "message": "Checkout completion rate dropped 34% vs baseline",
        "trace_id": "tr_a010",
    },
    {
        "timestamp": _ts(45),
        "service": "inventory-api",
        "level": "INFO",
        "message": "Stock reservation OK sku=SHOE-441",
        "trace_id": "tr_e011",
    },
]


def search_mock_logs(query: str, limit: int = 20) -> list[dict]:
    """Return mock logs relevant to the user query."""
    q = query.lower()
    keywords = []

    if any(w in q for w in ("checkout", "slow", "payment", "cart", "customer")):
        keywords.extend(["checkout", "payment", "slow", "timeout", "stripe", "cart", "abandon"])

    if any(w in q for w in ("error", "fail", "broken", "issue", "complain")):
        keywords.extend(["error", "fail", "timeout", "circuit"])

    if not keywords:
        keywords = q.split()

    scored: list[tuple[int, dict]] = []
    for log in MOCK_LOGS:
        text = f"{log['service']} {log['level']} {log['message']}".lower()
        score = sum(1 for kw in keywords if kw in text)
        if log["level"] == "ERROR":
            score += 2
        if score > 0:
            scored.append((score, log))

    scored.sort(key=lambda x: x[0], reverse=True)
    seen = set()
    results = []
    for _, log in scored:
        key = log["trace_id"] or log["message"]
        if key not in seen:
            seen.add(key)
            results.append(log)
        if len(results) >= limit:
            break

    if not results:
        results = [l for l in MOCK_LOGS if l["level"] in ("ERROR", "WARN")][:limit]

    return results
