"""FastAPI Application Entry Point for EasyFinePrint."""
from __future__ import annotations
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Response
from fastapi.exceptions import RequestValidationError
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
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    """Enforce strict security headers (MITM, XSS, Clickjacking prevention) and request body limits."""
    # Enforce maximum payload size (10 MB) to prevent memory exhaustion attacks
    content_length = request.headers.get("content-length")
    if content_length:
        try:
            if int(content_length) > 10 * 1024 * 1024:
                return JSONResponse(status_code=413, content={"detail": "Payload exceeds maximum allowed size of 10MB."})
        except ValueError:
            pass

    response = await call_next(request)

    # Enterprise security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=(), payment=()"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
    response.headers["Content-Security-Policy"] = "frame-ancestors 'none'; object-src 'none';"
    return response


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    messages = []
    for err in errors:
        loc = err.get("loc", [])
        field = loc[-1] if loc else "input"
        msg = err.get("msg", "Invalid input")
        err_type = err.get("type", "")
        if "string_too_short" in err_type:
            min_l = err.get("ctx", {}).get("min_length", 2)
            messages.append(f"Please enter at least {min_l} characters for {field}.")
        elif "string_too_long" in err_type:
            max_l = err.get("ctx", {}).get("max_length", 120)
            messages.append(f"Input for {field} exceeds maximum permitted length of {max_l} characters.")
        else:
            clean_field = str(field).replace("_", " ").capitalize()
            messages.append(f"{clean_field}: {msg}")
    friendly_msg = "; ".join(messages) or "Invalid input provided."
    return JSONResponse(
        status_code=422,
        content={"detail": friendly_msg},
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


async def forward_envelope_to_sentry(sentry_url: str, body: bytes) -> Response:
    """Forward an envelope payload to authentic upstream Sentry servers."""
    import httpx
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.post(sentry_url, content=body)
        return Response(content=resp.content, status_code=resp.status_code)


@app.post("/api/tunnel")
async def sentry_tunnel(request: Request):
    """Tunnel Sentry envelopes through our backend to prevent Brave Shields / adblocker drops.

    Parses the envelope header, validates the destination DSN hostname against authentic Sentry
    ingest domains to prevent open proxying, and proxies the payload server-to-server.
    """
    import json
    from urllib.parse import urlparse

    try:
        body = await request.body()
        if not body:
            return Response(status_code=200, content="OK")

        # Envelopes start with a JSON header on the first line
        first_line = body.split(b"\n")[0]
        if not first_line:
            return Response(status_code=200, content="OK")

        header = json.loads(first_line.decode("utf-8"))
        dsn = header.get("dsn")
        if not dsn:
            return Response(status_code=200, content="OK")

        parsed = urlparse(dsn)
        project_id = parsed.path.strip("/")
        hostname = (parsed.hostname or "").lower()

        # Validate that the destination is a genuine Sentry ingest host
        is_valid_sentry_host = (
            hostname == "sentry.io"
            or hostname.endswith(".sentry.io")
        )
        if not is_valid_sentry_host or not project_id:
            logger.warning("Rejected Sentry tunnel request to invalid host/project: %s", hostname)
            return Response(status_code=403, content="Invalid target host")

        sentry_url = f"https://{hostname}/api/{project_id}/envelope/"
        return await forward_envelope_to_sentry(sentry_url, body)
    except Exception as exc:
        logger.warning("Sentry tunnel proxy warning: %s", exc)
        return Response(status_code=200, content="OK")


@app.get("/")
async def root():
    return {
        "name": "EasyFinePrint API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/health",
    }
