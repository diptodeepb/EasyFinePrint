#!/usr/bin/env python3
"""
EasyFinePrint Unified Development Runner.
Starts FastAPI backend and Vite frontend concurrently with clean, color-prefixed logs
and strict credential redaction to prevent accidental token/URI leakage.
"""
from __future__ import annotations
import os
import re
import sys
import shutil
import signal
import subprocess
import threading
from typing import List, Set
from urllib.parse import urlparse

# ANSI terminal colors matching system / backend / frontend convention
COLORS = {
    "system": "\033[1;32m",    # Bold Green [system]
    "backend": "\033[1;34m",   # Bold Blue [backend]
    "frontend": "\033[1;33m",  # Bold Yellow [frontend]
    "error": "\033[1;31m",     # Bold Red [error]
    "reset": "\033[0m",
}

# Collect sensitive secret strings from environment and .env files for redaction
_SENSITIVE_STRINGS: Set[str] = set()

def _load_sensitive_strings():
    """Scan backend/.env and current os.environ for secret tokens to redact from console output."""
    global _SENSITIVE_STRINGS
    env_paths = [
        os.path.join(os.path.dirname(__file__), "backend", ".env"),
        os.path.join(os.path.dirname(__file__), ".env"),
    ]

    for ep in env_paths:
        if os.path.exists(ep):
            try:
                with open(ep, "r", encoding="utf-8", errors="ignore") as f:
                    for line in f:
                        line = line.strip()
                        if not line or line.startswith("#") or "=" not in line:
                            continue
                        k, v = line.split("=", 1)
                        k = k.strip()
                        v = v.strip().strip('"').strip("'")
                        if len(v) >= 5 and any(term in k.upper() for term in ("TOKEN", "KEY", "SECRET", "PASS", "ACCOUNT_ID", "URI")):
                            _SENSITIVE_STRINGS.add(v)
                            # If Mongo URI, also extract the raw password
                            if "://" in v and "@" in v:
                                try:
                                    parsed = urlparse(v)
                                    if parsed.password:
                                        _SENSITIVE_STRINGS.add(parsed.password)
                                except Exception:
                                    pass
            except Exception:
                pass

    for k, v in os.environ.items():
        if len(v) >= 5 and any(term in k.upper() for term in ("TOKEN", "KEY", "SECRET", "PASS", "ACCOUNT_ID")):
            _SENSITIVE_STRINGS.add(v)


_load_sensitive_strings()

# Regex patterns for credential sanitization
_RE_BEARER = re.compile(r"(Bearer\s+)[A-Za-z0-9_\-\.]{8,}", re.IGNORECASE)
_RE_MONGO_PASS = re.compile(r"(mongodb(?:\+srv)?://[^:]+:)([^@]+)(@)", re.IGNORECASE)
_RE_KV_SECRETS = re.compile(
    r"(?i)\b(api_key|token|api_token|secret|password|account_id)\b\s*[:=]\s*['\"]?([A-Za-z0-9_\-\.]{8,})['\"]?"
)


def redact_secrets(text: str) -> str:
    """Mask credentials, tokens, and sensitive URIs from console lines."""
    if not text:
        return text

    # Pattern replacements
    text = _RE_BEARER.sub(r"\1[REDACTED]", text)
    text = _RE_MONGO_PASS.sub(r"\1****\3", text)
    text = _RE_KV_SECRETS.sub(r"\1=[REDACTED]", text)

    # Literal secret replacements
    for s in _SENSITIVE_STRINGS:
        if s and s in text:
            text = text.replace(s, "[REDACTED]")

    return text


def log(prefix: str, msg: str, color_key: str = "system"):
    """Print prefixed, sanitized log message with ANSI formatting."""
    col = COLORS.get(color_key, COLORS["reset"])
    clean_msg = redact_secrets(msg)
    print(f"{col}[{prefix}]{COLORS['reset']} {clean_msg}", flush=True)


def find_backend_python() -> str:
    candidates = [
        os.path.join("backend", ".venv", "bin", "python3"),
        os.path.join("backend", ".venv", "bin", "python"),
        sys.executable,
    ]
    for path in candidates:
        if os.path.exists(path):
            try:
                res = subprocess.run(
                    [path, "-c", "import uvicorn, fastapi, trafilatura"],
                    capture_output=True,
                    text=True,
                )
                if res.returncode == 0:
                    return os.path.abspath(path)
            except Exception:
                continue
    return os.path.abspath(sys.executable)


def stream_logs(pipe, prefix: str, color_key: str):
    """Read subprocess stdout line-by-line, sanitize secrets, and print with prefix."""
    col = COLORS.get(color_key, COLORS["reset"])
    for raw_line in iter(pipe.readline, ""):
        if not raw_line:
            break
        sanitized = redact_secrets(raw_line.rstrip())
        print(f"{col}[{prefix}]{COLORS['reset']} {sanitized}", flush=True)
    pipe.close()


def main():
    log("system", "Starting EasyFinePrint development environment...", "system")

    # 1. Resolve Python environment
    py_bin = find_backend_python()
    log("system", f"Using Python: {py_bin}", "system")

    # 2. Check npm
    npm_bin = shutil.which("npm")
    if not npm_bin:
        log("error", "Error: npm is not found in PATH", "error")
        sys.exit(1)

    procs: List[subprocess.Popen] = []

    try:
        # Start Backend Server
        log("backend", "Starting FastAPI server on http://localhost:8000 ...", "backend")
        backend_proc = subprocess.Popen(
            [py_bin, "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"],
            cwd=os.path.abspath("backend"),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
        procs.append(backend_proc)
        t_be = threading.Thread(target=stream_logs, args=(backend_proc.stdout, "backend", "backend"), daemon=True)
        t_be.start()

        # Start Frontend Server
        log("frontend", "Starting Vite development server on http://localhost:5173 ...", "frontend")
        frontend_proc = subprocess.Popen(
            [npm_bin, "run", "dev"],
            cwd=os.path.abspath("frontend"),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
        procs.append(frontend_proc)
        t_fe = threading.Thread(target=stream_logs, args=(frontend_proc.stdout, "frontend", "frontend"), daemon=True)
        t_fe.start()

        log("system", "Both services running! Press Ctrl+C to terminate.", "system")
        backend_proc.wait()

    except KeyboardInterrupt:
        log("system", "Received termination signal. Stopping servers cleanly...", "system")
    finally:
        for p in procs:
            if p.poll() is None:
                p.terminate()
                try:
                    p.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    p.kill()
        log("system", "All development servers cleanly stopped.", "system")


if __name__ == "__main__":
    main()
