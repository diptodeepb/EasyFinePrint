"""Input/Output Sanitization Helpers (OWASP A05:2025, A10:2025, API10:2023)."""
from __future__ import annotations
import re
from typing import Any

# Strip ASCII control characters except tab, LF, CR (or strip all if allow_newlines=False)
_RE_CTRL_KEEP_NL = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
_RE_CTRL_ALL = re.compile(r"[\x00-\x1f\x7f]")
_RE_INTERNAL_PATHS = re.compile(r"(?:/[a-zA-Z0-9_.-]+){3,}(?:\.py|\.js|\.json)?")
_RE_URI_CREDS = re.compile(r"([a-zA-Z][a-zA-Z0-9+.-]*://[^:\s/]+:)([^@\s/]+)(@)")
_RE_BEARER = re.compile(r"(Bearer\s+)[A-Za-z0-9_\-\.]{6,}", re.IGNORECASE)


def contains_null_byte(val: Any) -> bool:
    return isinstance(val, str) and "\x00" in val


def strip_control_chars(text: Optional[str], allow_newlines: bool = True, max_length: Optional[int] = None) -> str:
    """Remove null bytes and unsafe ASCII control characters from strings."""
    if not text:
        return ""
    pattern = _RE_CTRL_KEEP_NL if allow_newlines else _RE_CTRL_ALL
    cleaned = pattern.sub("", str(text))
    if max_length is not None and len(cleaned) > max_length:
        cleaned = cleaned[:max_length]
    return cleaned


def sanitize_error_message(exc_or_msg: Any, fallback: str = "Upstream operation failed.") -> str:
    """Sanitize exception text before surfacing to API clients or persisting to DB."""
    if exc_or_msg is None:
        return fallback
    msg = strip_control_chars(str(exc_or_msg), allow_newlines=False)
    msg = _RE_BEARER.sub(r"\1[REDACTED]", msg)
    msg = _RE_URI_CREDS.sub(r"\1****\3", msg)
    msg = _RE_INTERNAL_PATHS.sub("[internal-path]", msg)
    msg = msg.strip()
    if not msg:
        return fallback
    if len(msg) > 240:
        msg = msg[:237] + "..."
    return msg
