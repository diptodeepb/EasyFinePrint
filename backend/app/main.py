"""FastAPI Application Entry Point for EasyFinePrint."""
from __future__ import annotations
import json
import logging
import re
import uuid
from contextlib import asynccontextmanager
from urllib.parse import urlparse
from fastapi import FastAPI, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.db.connection import create_indexes, close_connection
from app.routes import health, policies, discovery
from app.security.audit_logger import (
    log_security_event,
    redact_sensitive_text,
    reset_request_id,
    set_request_id,
)
from app.security.auth import is_trusted_origin
from app.security.rate_limiter import RateLimitExceeded, extract_client_ip, rate_limiter

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("easyfineprint")

# Silence httpx and httpcore request logging to prevent Sentry ingest URLs from leaking into console logs
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)

_RE_REQUEST_ID = re.compile(r"^[a-zA-Z0-9_-]{8,64}$")
_RE_SENTRY_HOST = re.compile(r"^(?:[a-z0-9-]+\.)*sentry\.io$")
_RE_SENTRY_PROJECT_ID = re.compile(r"^[0-9]{1,20}$")
_MUTATING_METHODS = {"POST", "PUT", "PATCH", "DELETE"}
_DOCS_PATHS = {"/docs", "/docs/oauth2-redirect", "/redoc", "/openapi.json"}

# Optional Sentry error monitoring with strict zero-PII redaction
if settings.sentry_dsn:
    try:
        import sentry_sdk

        def _strip_sensitive_data(event, hint):
            # 1. Force anonymous user with zeroed IP (prevents Sentry socket inference)
            event["user"] = {"ip_address": "0.0.0.0"}

            # 2. Scrub request metadata, headers, cookies, and payloads
            if "request" in event:
                req = event["request"]

                # Strip query strings from URLs to prevent leaking tokens or parameters
                if "query_string" in req:
                    req["query_string"] = ""
                if "url" in req and "?" in req["url"]:
                    req["url"] = req["url"].split("?")[0]

                # Strip cookies completely
                req.pop("cookies", None)

                # Keep only safe, non-identifying headers (explicitly excluding Authorization, X-Admin-Key, Cookie)
                safe_headers = {"host", "content-type", "accept", "accept-encoding", "x-request-id"}
                if "headers" in req:
                    req["headers"] = {
                        k: v for k, v in req["headers"].items()
                        if k.lower() in safe_headers
                    }

                # Redact body payload
                if "data" in req:
                    req["data"] = "[REDACTED]"

                # Strip ASGI client connection / socket environment
                req.pop("env", None)

            return event

        def _scrub_breadcrumb(crumb, hint):
            # Strip query strings from internal HTTP client calls
            if crumb.get("category") == "httpx":
                data = crumb.get("data", {})
                if "url" in data and "?" in data["url"]:
                    data["url"] = data["url"].split("?")[0]
            if isinstance(crumb.get("message"), str):
                crumb["message"] = redact_sensitive_text(crumb["message"])
            return crumb

        sentry_sdk.init(
            dsn=settings.sentry_dsn,
            environment=settings.environment,
            data_collection={"user_info": False},
            before_send=_strip_sensitive_data,
            before_breadcrumb=_scrub_breadcrumb,
            traces_sample_rate=0.1,
        )
        logger.info("Sentry monitoring initialized with strict zero-PII telemetry.")
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


docs_enabled_at_startup = settings.docs_enabled()

app = FastAPI(
    title="EasyFinePrint API",
    description="Evidence-backed monitor for public Terms of Service and Privacy Policy changes",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs" if docs_enabled_at_startup else None,
    redoc_url="/redoc" if docs_enabled_at_startup else None,
    openapi_url="/openapi.json" if docs_enabled_at_startup else None,
)


# CORS configuration supporting localhost, production, and scoped EasyFinePrint Vercel preview branch deployments
raw_origins = [
    settings.frontend_origin,
    "https://easyfineprint.vercel.app",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:4173",
    "http://127.0.0.1:4173",
]
parsed_origins = []
for entry in raw_origins:
    if entry:
        for o in entry.split(","):
            cleaned = o.strip().rstrip("/")
            if cleaned:
                parsed_origins.append(cleaned)

origins = sorted(list(set(parsed_origins)))
try:
    _origin_regex_compiled = re.compile(settings.allowed_origin_regex) if settings.allowed_origin_regex else None
except re.error:
    logger.warning("Invalid ALLOWED_ORIGIN_REGEX configured; disabling regex origin matching.")
    _origin_regex_compiled = None


def _resolve_body_limit(path: str) -> int:
    if path == "/api/tunnel":
        return settings.max_tunnel_body_bytes
    if path == "/api/discovery/search":
        return settings.max_discovery_body_bytes
    return settings.max_json_body_bytes


def _resolve_rate_limit_tier(method: str, path: str) -> str:
    if method == "POST":
        if path in ("/api/policies/analyze", "/api/policies/analyze-self") or path.endswith("/reanalyze"):
            return "analyze"
        if path.endswith("/check"):
            return "check"
        if path == "/api/discovery/search":
            return "discovery"
        if path == "/api/tunnel":
            return "tunnel"
    return "read"


class BodySizeLimitMiddleware:
    """Pure ASGI middleware enforcing streaming request body limits (including chunked requests)."""

    def __init__(self, app_asgi):
        self.app = app_asgi

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        path = scope.get("path", "")
        max_bytes = _resolve_body_limit(path)
        headers = {k.lower(): v for k, v in scope.get("headers", [])}
        content_length_raw = headers.get(b"content-length")
        if content_length_raw is not None:
            try:
                content_length = int(content_length_raw.decode("ascii"))
                if content_length < 0 or content_length > max_bytes:
                    resp = JSONResponse(
                        status_code=413,
                        content={"detail": f"Payload exceeds maximum allowed size of {max_bytes} bytes."},
                    )
                    _apply_security_headers(resp, path, "")
                    await resp(scope, receive, send)
                    return
            except (ValueError, UnicodeDecodeError):
                resp = JSONResponse(status_code=400, content={"detail": "Invalid Content-Length header."})
                _apply_security_headers(resp, path, "")
                await resp(scope, receive, send)
                return

        method = scope.get("method", "GET").upper()
        if method in ("GET", "HEAD", "OPTIONS") and content_length_raw is None:
            await self.app(scope, receive, send)
            return

        # Stream-count incoming chunks (handles Transfer-Encoding: chunked without Content-Length)
        buffered_messages = []
        received_bytes = 0
        more_body = True
        while more_body:
            message = await receive()
            msg_type = message.get("type")
            if msg_type == "http.request":
                chunk = message.get("body", b"")
                received_bytes += len(chunk)
                if received_bytes > max_bytes:
                    resp = JSONResponse(
                        status_code=413,
                        content={"detail": f"Payload exceeds maximum allowed size of {max_bytes} bytes."},
                    )
                    _apply_security_headers(resp, path, "")
                    await resp(scope, receive, send)
                    return
                buffered_messages.append(message)
                more_body = bool(message.get("more_body", False))
            else:
                buffered_messages.append(message)
                if msg_type == "http.disconnect":
                    break

        msg_iter = iter(buffered_messages)

        async def replay_receive():
            try:
                return next(msg_iter)
            except StopIteration:
                return await receive()

        await self.app(scope, replay_receive, send)


def _apply_security_headers(response: Response, path: str, request_id: str) -> None:
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=(), payment=()"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
    response.headers["Cross-Origin-Opener-Policy"] = "same-origin"
    response.headers["Cross-Origin-Resource-Policy"] = "cross-origin"
    response.headers["X-Permitted-Cross-Domain-Policies"] = "none"
    response.headers["X-API-Version"] = "1.0.0"
    if request_id:
        response.headers["X-Request-ID"] = request_id
    if path.startswith("/api/"):
        response.headers["Content-Security-Policy"] = "default-src 'none'; frame-ancestors 'none'; object-src 'none'; base-uri 'none'; form-action 'none';"
        response.headers["Cache-Control"] = "no-store, max-age=0"
    else:
        response.headers["Content-Security-Policy"] = "frame-ancestors 'none'; object-src 'none'; base-uri 'self';"


@app.middleware("http")
async def security_hardening_middleware(request: Request, call_next):
    """Enforce Request IDs, HTTP method hygiene, docs guard, CSRF/Origin checks, rate limits, and security headers."""
    raw_req_id = (request.headers.get("x-request-id") or "").strip()
    request_id = raw_req_id if _RE_REQUEST_ID.match(raw_req_id) else uuid.uuid4().hex
    req_token = set_request_id(request_id)
    path = request.url.path
    method = request.method.upper()

    try:
        # 1. Reject unsafe legacy HTTP methods (TRACE / TRACK)
        if method in ("TRACE", "TRACK"):
            log_security_event("unsafe_http_method_blocked", severity="WARNING", detail=f"Blocked {method}", request=request)
            resp = JSONResponse(status_code=405, content={"detail": "Method not allowed."})
            _apply_security_headers(resp, path, request_id)
            return resp

        # 2. Enforce production OpenAPI / Swagger docs disablement dynamically (OWASP API8/API9)
        if not settings.docs_enabled() and path in _DOCS_PATHS:
            resp = JSONResponse(status_code=404, content={"detail": "Not found."})
            _apply_security_headers(resp, path, request_id)
            return resp

        # 3. Origin / Fetch-Metadata CSRF guard on state-changing API requests (OWASP A01/A02)
        if method in _MUTATING_METHODS and path.startswith("/api/"):
            origin = (request.headers.get("origin") or "").strip()
            sec_fetch_site = (request.headers.get("sec-fetch-site") or "").strip().lower()
            if origin and not is_trusted_origin(origin, origins, _origin_regex_compiled):
                log_security_event(
                    "untrusted_origin_blocked",
                    severity="WARNING",
                    detail=f"Blocked mutating request from untrusted Origin: {origin}",
                    request=request,
                )
                resp = JSONResponse(status_code=403, content={"detail": "Origin not permitted."})
                _apply_security_headers(resp, path, request_id)
                return resp
            if sec_fetch_site == "cross-site" and (not origin or not is_trusted_origin(origin, origins, _origin_regex_compiled)):
                log_security_event(
                    "cross_site_csrf_blocked",
                    severity="WARNING",
                    detail="Blocked cross-site browser request without trusted Origin.",
                    request=request,
                )
                resp = JSONResponse(status_code=403, content={"detail": "Cross-site request rejected."})
                _apply_security_headers(resp, path, request_id)
                return resp

        # 4. Sliding-window per-IP rate limiting (OWASP API4/API6)
        rate_headers = {}
        if settings.rate_limit_enabled and path.startswith("/api/") and path != "/api/health":
            client_ip = extract_client_ip(request)
            tier = _resolve_rate_limit_tier(method, path)
            try:
                limit, remaining, reset_at = await rate_limiter.check(tier, client_ip)
                rate_headers = {
                    "X-RateLimit-Limit": str(limit),
                    "X-RateLimit-Remaining": str(remaining),
                    "X-RateLimit-Reset": str(reset_at),
                }
            except RateLimitExceeded as exc:
                log_security_event(
                    "rate_limit_exceeded",
                    severity="WARNING",
                    detail=str(exc),
                    request=request,
                    client_ip=client_ip,
                    extra={"tier": exc.tier},
                )
                resp = JSONResponse(
                    status_code=429,
                    content={"detail": f"Rate limit exceeded. Please retry after {exc.retry_after} seconds."},
                    headers={
                        "Retry-After": str(exc.retry_after),
                        "X-RateLimit-Limit": str(exc.limit),
                        "X-RateLimit-Remaining": "0",
                    },
                )
                _apply_security_headers(resp, path, request_id)
                return resp

        response = await call_next(request)
        _apply_security_headers(response, path, request_id)
        for hk, hv in rate_headers.items():
            response.headers[hk] = hv
        return response
    finally:
        reset_request_id(req_token)


# Pure ASGI body size limiter wraps inner app; CORSMiddleware wraps outermost so 403/413/429 still carry CORS headers
app.add_middleware(BodySizeLimitMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=settings.allowed_origin_regex or None,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"],
    allow_headers=["Content-Type", "Accept", "Authorization", "X-Admin-Key", "X-Request-ID", "X-Requested-With"],
    expose_headers=["X-Request-ID", "X-RateLimit-Limit", "X-RateLimit-Remaining", "X-RateLimit-Reset", "Retry-After", "X-API-Version"],
    max_age=86400,
)


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
        elif "extra_forbidden" in err_type:
            messages.append(f"Unexpected field '{field}' is not permitted.")
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
    logger.error("Unhandled exception at %s %s: %s", request.method, request.url.path, redact_sensitive_text(str(exc)), exc_info=True)
    log_security_event(
        "unhandled_server_exception",
        severity="ERROR",
        detail="Unhandled exception caught by global handler.",
        request=request,
    )
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred. Telemetry has been safely recorded."},
    )


# Register API routers under /api prefix
app.include_router(health.router, prefix="/api")
app.include_router(policies.router, prefix="/api")
app.include_router(discovery.router, prefix="/api")


async def forward_envelope_to_sentry(sentry_url: str, body: bytes) -> Response:
    """Forward an envelope payload to authentic upstream Sentry servers with redirects disabled."""
    import httpx
    async with httpx.AsyncClient(timeout=10.0, follow_redirects=False, verify=True) as client:
        resp = await client.post(sentry_url, content=body)
        return Response(content=resp.content, status_code=resp.status_code)


@app.post("/api/tunnel")
async def sentry_tunnel(request: Request):
    """Tunnel Sentry envelopes through our backend to prevent Brave Shields / adblocker drops.

    Parses the envelope header, strictly validates the destination DSN scheme, hostname, port,
    and numeric project ID to prevent SSRF / path traversal / open proxying.
    """
    try:
        body = await request.body()
        if len(body) > settings.max_tunnel_body_bytes:
            return Response(status_code=413, content="Envelope too large")
        if not body:
            return Response(status_code=200, content="OK")

        # Envelopes start with a JSON header on the first line
        first_line = body.split(b"\n", 1)[0]
        if not first_line:
            return Response(status_code=200, content="OK")

        header = json.loads(first_line.decode("utf-8"))
        if not isinstance(header, dict):
            return Response(status_code=400, content="Invalid envelope header")

        dsn = header.get("dsn")
        if not dsn or not isinstance(dsn, str):
            return Response(status_code=200, content="OK")

        parsed = urlparse(dsn.strip())
        project_id = parsed.path.strip("/")
        hostname = (parsed.hostname or "").lower().rstrip(".")

        is_valid_scheme = parsed.scheme.lower() == "https"
        is_valid_port = parsed.port is None
        is_valid_sentry_host = bool(_RE_SENTRY_HOST.match(hostname))
        is_valid_project_id = bool(_RE_SENTRY_PROJECT_ID.match(project_id))

        if not (is_valid_scheme and is_valid_port and is_valid_sentry_host and is_valid_project_id):
            log_security_event(
                "tunnel_invalid_target_rejected",
                severity="WARNING",
                detail=f"Rejected Sentry tunnel request to host={hostname}",
                request=request,
            )
            logger.warning("Rejected Sentry tunnel request to invalid host/project: %s", hostname)
            return Response(status_code=403, content="Invalid target host")

        sentry_url = f"https://{hostname}/api/{project_id}/envelope/"
        return await forward_envelope_to_sentry(sentry_url, body)
    except Exception as exc:
        logger.warning("Sentry tunnel proxy warning: %s", exc)
        return Response(status_code=200, content="OK")


@app.get("/")
async def root():
    payload = {
        "name": "EasyFinePrint API",
        "version": "1.0.0",
        "health": "/api/health",
    }
    if settings.docs_enabled():
        payload["docs"] = "/docs"
    return payload
