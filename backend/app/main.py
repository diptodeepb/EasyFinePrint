"""FastAPI Application Entry Point for EasyFinePrint."""
from __future__ import annotations
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.db.connection import create_indexes, close_connection
from app.routes import health, policies, discovery

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("easyfineprint")

# Optional Sentry error monitoring with redaction
if settings.sentry_dsn:
    try:
        import sentry_sdk

        def _strip_sensitive_data(event, hint):
            # Redact headers, query strings, and body data
            if "request" in event:
                req = event["request"]
                if "headers" in req:
                    req["headers"] = {k: "[REDACTED]" if "auth" in k.lower() or "cookie" in k.lower() else v for k, v in req["headers"].items()}
                if "data" in req:
                    req["data"] = "[REDACTED]"
            return event

        sentry_sdk.init(
            dsn=settings.sentry_dsn,
            environment=settings.environment,
            before_send=_strip_sensitive_data,
            traces_sample_rate=0.1,
        )
        logger.info("Sentry monitoring initialized with telemetry redaction.")
    except Exception as exc:
        logger.warning("Failed to initialize Sentry: %s", exc)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize DB indexes
    logger.info("Starting EasyFinePrint backend...")
    await create_indexes()
    yield
    # Shutdown: Cleanly close DB pool
    logger.info("Shutting down EasyFinePrint backend...")
    close_connection()


app = FastAPI(
    title="EasyFinePrint API",
    description="Evidence-backed monitor for public Terms of Service and Privacy Policy changes",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS configuration
origins = [
    settings.frontend_origin,
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]
# Avoid duplicates
origins = list(set([o.rstrip("/") for o in origins if o]))

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled exception at %s %s: %s", request.method, request.url.path, exc, exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred. Telemetry has been safely recorded."},
    )


# Register API routers under /api prefix
app.include_router(health.router, prefix="/api")
app.include_router(policies.router, prefix="/api")
app.include_router(discovery.router, prefix="/api")


@app.get("/")
async def root():
    return {
        "name": "EasyFinePrint API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/health",
    }
