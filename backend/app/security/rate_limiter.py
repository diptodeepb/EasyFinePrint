"""Sliding-Window Rate Limiter for Resource & Business-Flow Protection (OWASP API4:2023, API6:2023)."""
from __future__ import annotations
import asyncio
import os
import time
from collections import OrderedDict, deque
from typing import Deque, Dict, Optional, Tuple
from fastapi import Request

from app.config import settings


class RateLimitExceeded(Exception):
    """Raised when a client exceeds the configured request rate limit."""
    def __init__(self, limit: int, window_seconds: int, retry_after: int, tier: str):
        self.limit = limit
        self.window_seconds = window_seconds
        self.retry_after = max(1, retry_after)
        self.tier = tier
        super().__init__(f"Rate limit exceeded for '{tier}'. Retry after {self.retry_after}s.")


# Tier configurations: (max_requests, window_seconds)
RATE_LIMIT_TIERS: Dict[str, Tuple[int, int]] = {
    "analyze": (20, 60),       # Expensive scraping + LLM evaluation
    "check": (30, 60),         # Live fetch + diffing
    "discovery": (30, 60),     # Directory + live crawling
    "tunnel": (60, 60),        # Sentry envelope relay
    "admin_auth": (10, 60),    # Failed admin auth brute-force protection
    "read": (180, 60),         # Standard GET endpoints
}


def extract_client_ip(request: Request) -> str:
    """
    Extract client IP safely.
    Only trusts forwarding headers when TRUST_PROXY_HEADERS=true or running inside Vercel's edge runtime (VERCEL=1).
    """
    on_vercel = os.environ.get("VERCEL") == "1" or bool(os.environ.get("VERCEL_ENV"))
    if settings.trust_proxy_headers or on_vercel:
        vercel_ip = request.headers.get("x-vercel-forwarded-for")
        if vercel_ip:
            first = vercel_ip.split(",")[0].strip()
            if first:
                return first
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip.strip()
        xff = request.headers.get("x-forwarded-for")
        if xff:
            parts = [p.strip() for p in xff.split(",") if p.strip()]
            if parts:
                return parts[0] if on_vercel else parts[-1]
    if request.client and request.client.host:
        return request.client.host
    return "unknown"


class SlidingWindowRateLimiter:
    """Memory-bounded async sliding-window rate limiter keyed by (tier, client_ip)."""

    def __init__(self, max_keys: int = 10000):
        self._max_keys = max_keys
        self._buckets: OrderedDict[Tuple[str, str], Deque[float]] = OrderedDict()
        self._lock = asyncio.Lock()

    def clear(self) -> None:
        self._buckets.clear()

    async def check(
        self,
        tier: str,
        client_ip: str,
        limit_override: Optional[int] = None,
        window_override: Optional[int] = None,
    ) -> Tuple[int, int, int]:
        """
        Record a hit and verify rate limit.
        Returns (limit, remaining, reset_epoch_seconds).
        Raises RateLimitExceeded if quota exhausted.
        """
        default_limit, default_window = RATE_LIMIT_TIERS.get(tier, (120, 60))
        limit = limit_override if limit_override is not None else default_limit
        window = window_override if window_override is not None else default_window

        now = time.monotonic()
        wall_now = int(time.time())
        cutoff = now - window
        key = (tier, client_ip)

        async with self._lock:
            dq = self._buckets.get(key)
            if dq is None:
                # Evict oldest buckets if capacity reached to prevent OOM DoS
                while len(self._buckets) >= self._max_keys:
                    self._buckets.popitem(last=False)
                dq = deque()
                self._buckets[key] = dq
            else:
                self._buckets.move_to_end(key)

            while dq and dq[0] <= cutoff:
                dq.popleft()

            if len(dq) >= limit:
                oldest = dq[0]
                retry_after = int(window - (now - oldest)) + 1
                raise RateLimitExceeded(limit=limit, window_seconds=window, retry_after=retry_after, tier=tier)

            dq.append(now)
            remaining = max(0, limit - len(dq))
            reset_at = wall_now + window
            return limit, remaining, reset_at


rate_limiter = SlidingWindowRateLimiter()
