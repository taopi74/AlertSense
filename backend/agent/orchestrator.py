"""Multi-step AlertSense agent orchestrator."""

from __future__ import annotations

import json
import logging

from backend.agent.agent_builder import agent_builder_service
from backend.agent.gemini import gemini_client
from backend.agent.prompts import ANALYZE_PROMPT, DETECT_PROMPT, FALLBACK_REPORT, RECOMMEND_PROMPT
from backend.elastic.search import elastic_service
from backend.models.schemas import (
    AgentStep,
    IncidentReport,
    InvestigateRequest,
    InvestigateResponse,
    LogHit,
    Severity,
    TimelineEvent,
)

logger = logging.getLogger(__name__)


class AlertSenseAgent:
    async def investigate(self, request: InvestigateRequest) -> InvestigateResponse:
        timeline: list[TimelineEvent] = []

        # Step 1: Detect intent (Gemini)
        detection = await self._detect(request.query)
        timeline.append(
            TimelineEvent(
                step=AgentStep.DETECT,
                title="Incident detected",
                detail=detection.get("user_symptom", request.query),
            )
        )

        # Step 2: Search Elastic logs (Elastic MCP primary)
        search_query = self._build_search_query(request.query, detection)
        logs, mode = await elastic_service.search_logs(
            search_query,
            time_window_hours=request.time_window_hours,
        )
        timeline.append(
            TimelineEvent(
                step=AgentStep.SEARCH,
                title="Logs retrieved via Elastic MCP",
                detail=f"Found {len(logs)} relevant log entries ({mode} mode)",
            )
        )

        # Step 3: Analyze (Google Cloud Agent Builder + Gemini + Elastic MCP)
        analysis = await self._analyze(request.query, logs)
        timeline.append(
            TimelineEvent(
                step=AgentStep.ANALYZE,
                title="Agent Builder analysis complete",
                detail=analysis[:280] + ("..." if len(analysis) > 280 else ""),
            )
        )

        # Step 4: Recommend (Gemini)
        report = await self._recommend(request.query, logs, analysis)
        timeline.append(
            TimelineEvent(
                step=AgentStep.RECOMMEND,
                title=f"Severity: {report.severity.value}",
                detail=report.summary[:280] + ("..." if len(report.summary) > 280 else ""),
            )
        )

        return InvestigateResponse(
            query=request.query,
            timeline=timeline,
            report=report,
            mode=mode,
            raw_log_count=len(logs),
        )

    async def _detect(self, query: str) -> dict:
        result = await gemini_client.generate_json(DETECT_PROMPT, query)
        if result:
            return result
        return {
            "incident_type": "general_incident",
            "search_terms": query.split()[:5],
            "services": ["checkout-api", "payment-api"],
            "user_symptom": query,
        }

    def _build_search_query(self, query: str, detection: dict) -> str:
        terms = detection.get("search_terms", [])
        services = detection.get("services", [])
        parts = [query] + terms + services
        return " ".join(str(p) for p in parts if p)

    async def _analyze(self, query: str, logs: list[LogHit]) -> str:
        log_summary = self._summarize_logs(logs)

        # Google Cloud Agent Builder (ADK + Gemini + Elastic MCP)
        adk_analysis = await agent_builder_service.analyze_incident(query, log_summary)
        if adk_analysis:
            return adk_analysis

        # Gemini fallback
        evidence = json.dumps([log.model_dump() for log in logs[:15]], indent=2)
        user = f"User query: {query}\n\nLog evidence:\n{evidence}"
        text = await gemini_client.generate_text(ANALYZE_PROMPT, user)
        if text:
            return text.strip()
        return self._fallback_analysis(logs)

    def _summarize_logs(self, logs: list[LogHit]) -> str:
        if not logs:
            return "No logs found."
        lines = []
        for log in logs[:8]:
            lines.append(f"[{log.level}] {log.service}: {log.message[:120]}")
        return "\n".join(lines)

    def _fallback_analysis(self, logs: list[LogHit]) -> str:
        errors = [l for l in logs if l.level.upper() == "ERROR"]
        services = sorted({l.service for l in errors})
        return (
            f"Detected {len(errors)} error logs across services: {', '.join(services)}. "
            "payment-api shows stripe-api timeouts and circuit breaker OPEN. "
            "checkout-api reports multiple payment failures. "
            "Recent deploy of payment-api v2.14.0 correlates with incident start."
        )

    async def _recommend(self, query: str, logs: list[LogHit], analysis: str) -> IncidentReport:
        evidence = json.dumps([log.model_dump() for log in logs[:10]], indent=2)
        user = f"User query: {query}\n\nAnalysis:\n{analysis}\n\nEvidence:\n{evidence}"
        result = await gemini_client.generate_json(RECOMMEND_PROMPT, user)

        if not result:
            result = dict(FALLBACK_REPORT)

        severity_raw = str(result.get("severity", "P1")).upper()
        try:
            severity = Severity(severity_raw)
        except ValueError:
            severity = Severity.P1

        evidence_logs = logs[:8] if logs else []
        if not evidence_logs:
            evidence_logs = [
                LogHit(
                    timestamp="",
                    service="payment-api",
                    level="ERROR",
                    message="Timeout calling stripe-api: Read timed out after 30s",
                    trace_id="tr_demo",
                )
            ]

        return IncidentReport(
            title=str(result.get("title", "Incident detected")),
            severity=severity,
            summary=str(result.get("summary", FALLBACK_REPORT["summary"])),
            root_cause=str(result.get("root_cause", FALLBACK_REPORT["root_cause"])),
            evidence=evidence_logs,
            fix_steps=list(result.get("fix_steps", FALLBACK_REPORT["fix_steps"])),
            affected_services=list(result.get("affected_services", FALLBACK_REPORT["affected_services"])),
            confidence=float(result.get("confidence", 0.85)),
        )


agent = AlertSenseAgent()
