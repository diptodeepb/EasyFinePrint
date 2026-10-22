"""Health check endpoint with strict information-disclosure protection."""
from __future__ import annotations
from datetime import datetime, timezone
from fastapi import APIRouter
from app.db.connection import check_db_health

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check():
    """Returns minimal safe service readiness status without infrastructure telemetry."""
    db_ok = await check_db_health()
    return {
        "status": "healthy" if db_ok else "degraded",
        "service": "EasyFinePrint",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
