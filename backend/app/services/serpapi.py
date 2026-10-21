"""SerpApi Discovery Service with Strict Quota Guard and Caching.

Allows users to discover official policy URLs for companies/services when they
do not have the direct URL. Strictly optional, capped, and disabled by default.
"""
from __future__ import annotations
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
import httpx
from app.config import settings

logger = logging.getLogger("easyfineprint.serpapi")

# In-memory cache for query results: normalized_query -> (candidates, timestamp)
_query_cache: Dict[str, Tuple[List[Dict[str, Any]], datetime]] = {}
# Hourly usage tracking: hour_bucket -> count
_hourly_usage: Dict[str, int] = {}
# Monthly usage tracking: month_bucket -> count
_monthly_usage: Dict[str, int] = {}


def _get_hour_bucket() -> str:
    now = datetime.now(timezone.utc)
    return now.strftime("%Y-%m-%d-%H")


def _get_month_bucket() -> str:
    now = datetime.now(timezone.utc)
    return now.strftime("%Y-%m")


async def check_serpapi_account_status() -> Optional[Dict[str, Any]]:
    """Inspect remaining searches and throughput from SerpApi Account API."""
    if not settings.serpapi_api_key:
        return None

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(
                "https://serpapi.com/account.json",
                params={"api_key": settings.serpapi_api_key},
            )
            if resp.status_code == 200:
                data = resp.json()
                return {
                    "plan_searches_left": data.get("plan_searches_left"),
                    "this_month_usage": data.get("this_month_usage"),
                    "account_rate_limit_per_hour": data.get("account_rate_limit_per_hour"),
                }
    except Exception as exc:
        logger.debug("Failed to query SerpApi account API: %s", exc)
    return None


async def discover_policy_urls(query: str) -> Dict[str, Any]:
    """
    Search for candidate legal policy URLs for a company or service.
    Returns { candidates: [...], cached: bool, quota_remaining: int }.
    """
    if not settings.serpapi_enabled or not settings.serpapi_api_key:
        return {
            "error": "serpapi_disabled",
            "message": "Policy discovery search is disabled. Please enter the official policy URL directly.",
            "candidates": [],
        }

    norm_query = query.strip().lower()
    search_term = f"{norm_query} terms of service OR privacy policy"

    # 1. Check in-memory cache
    if norm_query in _query_cache:
        cached_candidates, _ = _query_cache[norm_query]
        logger.info("Serving policy discovery from cache for query: '%s'", norm_query)
        return {
            "candidates": cached_candidates,
            "cached": True,
            "quota_remaining": settings.serpapi_monthly_cap - _monthly_usage.get(_get_month_bucket(), 0),
        }

    # 2. Check quota limits
    h_bucket = _get_hour_bucket()
    m_bucket = _get_month_bucket()

    curr_hourly = _hourly_usage.get(h_bucket, 0)
    curr_monthly = _monthly_usage.get(m_bucket, 0)

    if curr_hourly >= settings.serpapi_hourly_cap:
        logger.warning("SerpApi hourly cap reached (%d/%d)", curr_hourly, settings.serpapi_hourly_cap)
        return {
            "error": "hourly_cap_exhausted",
            "message": "Hourly discovery search cap reached. Please enter the policy URL directly.",
            "candidates": [],
        }

    if curr_monthly >= settings.serpapi_monthly_cap:
        logger.warning("SerpApi monthly cap reached (%d/%d)", curr_monthly, settings.serpapi_monthly_cap)
        return {
            "error": "monthly_cap_exhausted",
            "message": "Monthly discovery search cap reached. Please enter the policy URL directly.",
            "candidates": [],
        }

    # 3. Execute search via SerpApi
    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            resp = await client.get(
                "https://serpapi.com/search.json",
                params={
                    "engine": "google",
                    "q": search_term,
                    "api_key": settings.serpapi_api_key,
                    "num": 5,
                },
            )

            if resp.status_code != 200:
                logger.warning("SerpApi returned error %d", resp.status_code)
                return {
                    "error": "upstream_error",
                    "message": "Search provider was unavailable. Please enter the policy URL directly.",
                    "candidates": [],
                }

            # Increment usage counters
            _hourly_usage[h_bucket] = curr_hourly + 1
            _monthly_usage[m_bucket] = curr_monthly + 1

            data = resp.json()
            organic_results = data.get("organic_results", [])

            candidates = []
            for item in organic_results[:5]:
                link = item.get("link")
                title = item.get("title", "Policy Document")
                snippet = item.get("snippet", "")

                if link and (link.startswith("http://") or link.startswith("https://")):
                    candidates.append({
                        "title": title,
                        "url": link,
                        "snippet": snippet,
                        "source": "serpapi",
                    })

            # Store in cache
            _query_cache[norm_query] = (candidates, datetime.now(timezone.utc))

            return {
                "candidates": candidates,
                "cached": False,
                "quota_remaining": max(0, settings.serpapi_monthly_cap - _monthly_usage[m_bucket]),
            }

    except Exception as exc:
        logger.warning("SerpApi request exception: %s", exc)
        return {
            "error": "search_failed",
            "message": "Failed to complete discovery search. Please enter the URL directly.",
            "candidates": [],
        }
