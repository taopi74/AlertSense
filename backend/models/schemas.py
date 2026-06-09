"""Pydantic models for AlertSense API."""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class Severity(str, Enum):
    P0 = "P0"
    P1 = "P1"
    P2 = "P2"
    INFO = "INFO"


class AgentStep(str, Enum):
    DETECT = "detect"
    SEARCH = "search"
    ANALYZE = "analyze"
    RECOMMEND = "recommend"


class TimelineEvent(BaseModel):
    step: AgentStep
    title: str
    detail: str
    status: str = "complete"


class LogHit(BaseModel):
    timestamp: str
    service: str
    level: str
    message: str
    trace_id: str | None = None


class IncidentReport(BaseModel):
    title: str
    severity: Severity
    summary: str
    root_cause: str
    evidence: list[LogHit] = Field(default_factory=list)
    fix_steps: list[str] = Field(default_factory=list)
    affected_services: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0, le=1, default=0.85)


class InvestigateRequest(BaseModel):
    query: str = Field(..., min_length=3, max_length=2000)
    time_window_hours: int = Field(default=24, ge=1, le=168)


class InvestigateResponse(BaseModel):
    query: str
    timeline: list[TimelineEvent]
    report: IncidentReport
    mode: str
    raw_log_count: int


class HealthResponse(BaseModel):
    status: str
    mode: str
    gemini_configured: bool
    elastic_configured: bool
    agent_builder_configured: bool = False
    version: str = "1.0.0"
    python_version: str | None = None
    import_error: str | None = None


class ConfigResponse(BaseModel):
    mode: str
    gemini_model: str
    elastic_mcp_configured: bool
    elasticsearch_configured: bool
    agent_builder_configured: bool = False
    demo_available: bool
