"""Health check and dependency diagnostics endpoint."""
from __future__ import annotations
from datetime import datetime, timezone
from fastapi import APIRouter
from app.config import settings
from app.db.connection import check_db_health

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check():
    """Returns service readiness, non-sensitive dependency status, and environment."""
    db_ok = await check_db_health()
    return {
        "status": "healthy",
        "service": "EasyFinePrint",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "environment": settings.environment,
        "database": "connected" if db_ok else "in_memory_fallback",
        "ai_service": "configured" if settings.gemini_api_key else "fallback_only",
        "serpapi_discovery": "enabled" if (settings.serpapi_enabled and settings.serpapi_api_key) else "disabled",
    }
