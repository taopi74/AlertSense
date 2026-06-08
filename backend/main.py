"""AlertSense API — Elastic track hackathon project."""

from __future__ import annotations

import logging
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from backend.agent.orchestrator import agent
from backend.config import settings
from backend.models.schemas import (
    ConfigResponse,
    HealthResponse,
    InvestigateRequest,
    InvestigateResponse,
)

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AlertSense",
    description="AI incident triage agent — Elastic MCP + Gemini",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list + ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    mode = "demo" if settings.use_demo else "elastic"
    return HealthResponse(
        status="ok",
        mode=mode,
        gemini_configured=settings.gemini_configured,
        elastic_configured=settings.elastic_mcp_configured or settings.elasticsearch_configured,
    )


@app.get("/api/config", response_model=ConfigResponse)
async def config() -> ConfigResponse:
    return ConfigResponse(
        mode="demo" if settings.use_demo else "elastic",
        gemini_model=settings.gemini_model,
        elastic_mcp_configured=settings.elastic_mcp_configured,
        elasticsearch_configured=settings.elasticsearch_configured,
        demo_available=True,
    )


@app.post("/api/investigate", response_model=InvestigateResponse)
async def investigate(request: InvestigateRequest) -> InvestigateResponse:
    try:
        return await agent.investigate(request)
    except Exception as exc:
        logger.exception("Investigation failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


# Serve built frontend in production
FRONTEND_DIST = Path(__file__).resolve().parent.parent / "frontend" / "dist"
if FRONTEND_DIST.exists():
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIST / "assets"), name="assets")

    @app.get("/")
    async def serve_spa():
        return FileResponse(FRONTEND_DIST / "index.html")

    @app.get("/{full_path:path}")
    async def spa_fallback(full_path: str):
        file_path = FRONTEND_DIST / full_path
        if file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(FRONTEND_DIST / "index.html")
