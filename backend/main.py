"""AlertSense API — Elastic track hackathon project."""

from __future__ import annotations

import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import APIRouter, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from backend.agent.agent_builder import agent_builder_service
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

IS_VERCEL = bool(os.environ.get("VERCEL"))

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

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    import sys
    mode = "demo" if settings.use_demo else "elastic"
    import_err = getattr(agent_builder_service, "import_error", None)
    
    adk_ver = None
    try:
        import google.adk
        adk_ver = getattr(google.adk, "__version__", None)
    except Exception:
        pass

    return HealthResponse(
        status="ok",
        mode=mode,
        gemini_configured=settings.gemini_configured,
        elastic_configured=settings.elastic_mcp_configured or settings.elasticsearch_configured,
        agent_builder_configured=agent_builder_service.configured,
        python_version=sys.version,
        import_error=import_err,
        adk_version=adk_ver,
    )


@router.get("/config", response_model=ConfigResponse)
async def config() -> ConfigResponse:
    return ConfigResponse(
        mode="demo" if settings.use_demo else "elastic",
        gemini_model=settings.gemini_model,
        elastic_mcp_configured=settings.elastic_mcp_configured,
        elasticsearch_configured=settings.elasticsearch_configured,
        agent_builder_configured=agent_builder_service.configured,
        demo_available=True,
    )


@router.post("/investigate", response_model=InvestigateResponse)
async def investigate(request: InvestigateRequest) -> InvestigateResponse:
    try:
        return await agent.investigate(request)
    except Exception as exc:
        logger.exception("Investigation failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


# Standard paths used locally and in production
app.include_router(router, prefix="/api")
# Vercel Services may forward stripped paths (/health instead of /api/health)
app.include_router(router)


# Serve built frontend locally (not on Vercel — static files served separately)
FRONTEND_DIST = Path(__file__).resolve().parent.parent / "frontend" / "dist"

if FRONTEND_DIST.exists() and not IS_VERCEL:
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
