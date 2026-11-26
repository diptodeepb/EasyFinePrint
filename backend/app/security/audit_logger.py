"""Structured Security Audit Logging & Correlation ID Management (OWASP A09:2025)."""
from __future__ import annotations
import contextvars
import hashlib
import json
import logging
import re
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from fastapi import Request

security_logger = logging.getLogger("easyfineprint.security")

_request_id_ctx: contextvars.ContextVar[str] = contextvars.ContextVar("request_id", default="")

_RE_BEARER = re.compile(r"(Bearer\s+)[A-Za-z0-9_\-\.]{6,}", re.IGNORECASE)
_RE_URI_CREDS = re.compile(r"([a-zA-Z][a-zA-Z0-9+.-]*://[^:\s/]+:)([^@\s/]+)(@)")
_RE_KV_SECRET = re.compile(
    r"(?i)\b(api_key|api_token|token|secret|password|admin_key|x-admin-key|dsn)\b\s*[:=]\s*['\"]?([^\s,'\";]{6,})['\"]?"
)


def set_request_id(request_id: str) -> contextvars.Token:
    return _request_id_ctx.set(request_id)


def reset_request_id(token: contextvars.Token) -> None:
    _request_id_ctx.reset(token)


def get_request_id() -> str:
    return _request_id_ctx.get()


def redact_sensitive_text(text: str) -> str:
    """Scrub credentials, bearer tokens, and URI passwords from loggable strings."""
    if not text:
        return ""
    cleaned = _RE_BEARER.sub(r"\1[REDACTED]", str(text))
    cleaned = _RE_URI_CREDS.sub(r"\1****\3", cleaned)
    cleaned = _RE_KV_SECRET.sub(r"\1=[REDACTED]", cleaned)
    return cleaned


def anonymize_ip(ip_str: Optional[str]) -> str:
    """Return a privacy-preserving hash prefix for client IPs in audit logs."""
    if not ip_str:
        return "unknown"
    digest = hashlib.sha256(ip_str.encode("utf-8", errors="ignore")).hexdigest()[:12]
    return f"ip_{digest}"


def log_security_event(
    event_type: str,
    severity: str = "WARNING",
    detail: str = "",
    request: Optional[Request] = None,
    client_ip: Optional[str] = None,
    extra: Optional[Dict[str, Any]] = None,
) -> None:
    """Emit a structured JSON security event log without leaking PII or secrets."""
    payload: Dict[str, Any] = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event_type": event_type,
        "severity": severity.upper(),
        "request_id": get_request_id() or None,
    }
    if request is not None:
        payload["method"] = request.method
        payload["path"] = request.url.path
        if not client_ip and request.client:
            client_ip = request.client.host
    if client_ip:
        payload["client_ref"] = anonymize_ip(client_ip)
    if detail:
        payload["detail"] = redact_sensitive_text(detail)[:500]
    if extra:
        safe_extra = {}
        for k, v in extra.items():
            safe_extra[str(k)] = redact_sensitive_text(str(v))[:200] if v is not None else None
        payload["extra"] = safe_extra

    level = getattr(logging, severity.upper(), logging.WARNING)
    security_logger.log(level, "SECURITY_EVENT %s", json.dumps(payload, separators=(",", ":")))
