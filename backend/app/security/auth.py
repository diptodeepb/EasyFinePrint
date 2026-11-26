"""Authentication, Function-Level Authorization, and Origin/CSRF Guards (OWASP A01, A07, API1, API2, API5)."""
from __future__ import annotations
import hmac
from typing import Iterable, Optional
from fastapi import HTTPException, Request

from app.config import settings
from app.security.audit_logger import log_security_event
from app.security.rate_limiter import extract_client_ip, rate_limiter, RateLimitExceeded


def _extract_bearer_token(auth_header: Optional[str]) -> Optional[str]:
    if not auth_header:
        return None
    parts = auth_header.strip().split(None, 1)
    if len(parts) == 2 and parts[0].lower() == "bearer":
        return parts[1].strip()
    return None


async def require_admin_access(request: Request) -> None:
    """
    Enforce function-level access control on administrative/destructive endpoints (e.g. DELETE).

    - When ADMIN_API_KEY is configured (any environment): requires constant-time match via
      `X-Admin-Key` or `Authorization: Bearer <key>`. Brute-force attempts are rate-limited.
    - When ENVIRONMENT == 'production' and ADMIN_API_KEY is unconfigured: fails closed (403).
    - When ENVIRONMENT != 'production' and ADMIN_API_KEY is unconfigured: allowed for local dev/test
      unless REQUIRE_ADMIN_KEY=true.
    """
    configured_key = (settings.admin_api_key or "").strip()
    is_prod = (settings.environment or "").strip().lower() == "production"

    if not configured_key:
        if is_prod or settings.require_admin_key:
            log_security_event(
                "admin_access_disabled",
                severity="WARNING",
                detail="Destructive administrative action blocked: ADMIN_API_KEY is not configured.",
                request=request,
            )
            raise HTTPException(
                status_code=403,
                detail="Administrative operation is disabled in this environment.",
            )
        return

    client_ip = extract_client_ip(request)
    provided_key = (
        request.headers.get("x-admin-key")
        or _extract_bearer_token(request.headers.get("authorization"))
        or ""
    ).strip()

    if not provided_key:
        try:
            await rate_limiter.check("admin_auth", client_ip)
        except RateLimitExceeded as exc:
            raise HTTPException(
                status_code=429,
                detail="Too many failed authentication attempts. Please try again later.",
                headers={"Retry-After": str(exc.retry_after)},
            )
        log_security_event(
            "admin_auth_missing",
            severity="WARNING",
            detail="Missing administrative credentials for protected endpoint.",
            request=request,
            client_ip=client_ip,
        )
        raise HTTPException(
            status_code=401,
            detail="Authentication required for this operation.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not hmac.compare_digest(provided_key.encode("utf-8"), configured_key.encode("utf-8")):
        try:
            await rate_limiter.check("admin_auth", client_ip)
        except RateLimitExceeded as exc:
            raise HTTPException(
                status_code=429,
                detail="Too many failed authentication attempts. Please try again later.",
                headers={"Retry-After": str(exc.retry_after)},
            )
        log_security_event(
            "admin_auth_failed",
            severity="WARNING",
            detail="Invalid administrative credentials supplied.",
            request=request,
            client_ip=client_ip,
        )
        raise HTTPException(
            status_code=403,
            detail="Forbidden: invalid credentials.",
        )


def is_trusted_origin(origin: str, allowed_origins: Iterable[str], origin_regex_pattern) -> bool:
    """Check whether an Origin header matches the explicit allowlist or scoped preview regex."""
    if not origin:
        return False
    cleaned = origin.strip().rstrip("/")
    if cleaned in allowed_origins:
        return True
    if origin_regex_pattern is not None and origin_regex_pattern.match(cleaned):
        return True
    return False
