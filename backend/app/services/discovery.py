"""Company Legal Policy Discovery Service.

Discovers official Terms of Service, Privacy Policy, and User Agreement URLs for
companies and web services using a combination of an expansive authoritative directory
and multi-tier dynamic discovery (DOM crawling, canonical legal path probing,
and search engine fallback). Enforces strict multi-hop SSRF validation.
"""
from __future__ import annotations
import logging
import re
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import httpx
from app.services.url_guard import validate_url, resolve_and_verify_hostname, URLValidationError
from app.services.known_directory import KNOWN_DIRECTORY, DIRECTORY_ALIASES, search_known_directory

logger = logging.getLogger("easyfineprint.discovery")

# In-memory query cache: normalized_query -> (candidates, timestamp)
_query_cache: Dict[str, tuple[List[Dict[str, Any]], datetime]] = {}

# Configurable upper limit for auto-discovered candidate legal resources per company
MAX_DISCOVERY_CANDIDATES = 15

# Common canonical legal endpoint paths probed during dynamic inspection
CANONICAL_LEGAL_PATHS = [
    ("/terms", "Terms of Service"),
    ("/privacy", "Privacy Policy"),
    ("/terms-of-service", "Terms of Service"),
    ("/privacy-policy", "Privacy Policy"),
    ("/terms-of-use", "Terms of Use"),
    ("/user-agreement", "User Agreement"),
    ("/legal", "Legal Notices & Terms"),
    ("/legal/terms", "Terms of Service"),
    ("/legal/privacy", "Privacy Policy"),
    ("/legal/terms-of-service", "Terms of Service"),
    ("/legal/privacy-policy", "Privacy Policy"),
    ("/legal/user-agreement", "User Agreement"),
    ("/acceptable-use", "Acceptable Use Policy"),
    ("/cookies", "Cookie Policy"),
    ("/security", "Security & Trust Policy"),
]

# Standard request headers mimicking modern desktop browser
BROWSER_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}


def _normalize_title(raw_title: str, default_title: str = "Legal Document") -> str:
    """Format and clean raw anchor text or heading into a professional legal document title."""
    clean = re.sub(r"\s+", " ", raw_title).strip()
    if not clean or len(clean) < 3 or len(clean) > 80:
        return default_title
    # Filter out junk titles like "Click here", "More info"
    lower = clean.lower()
    if lower in ("here", "click here", "link", "learn more", "more", "read more"):
        return default_title
    return clean.title() if clean.islower() else clean


def _prioritize_policies(candidates: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """
    Sort candidate policies logically:
    1. Core Terms of Service / Terms of Use / User Agreement
    2. Privacy Policy / Privacy Statement / Privacy Notice
    3. Cookie Policy
    4. Acceptable Use Policy
    5. Developer / API Terms
    6. Security & Trust Policy
    7. Other policies
    """
    def _rank(item: Dict[str, str]) -> int:
        title = item.get("title", "").lower()
        url = item.get("url", "").lower()
        combined = f"{title} {url}"

        # 1. Core Terms of Service / User Agreement
        if any(kw in combined for kw in ("terms of service", "terms of use", "user agreement", "conditions of use", "service agreement", "terms and conditions")):
            return 1
        # 2. Privacy Policy / Statement
        if "privacy" in combined:
            return 2
        # 3. Cookie Policy
        if "cookie" in combined:
            return 3
        # 4. Acceptable Use
        if "acceptable" in combined or "aup" in combined:
            return 4
        # 5. Developer / API terms or generic terms
        if "developer" in combined or "api" in combined or "terms" in combined or "tos" in combined:
            return 5
        # 6. Security & Trust
        if "security" in combined:
            return 6
        return 7

    return sorted(candidates, key=_rank)


async def crawl_homepage_for_policy_links(base_url: str) -> List[Dict[str, str]]:
    """
    Safely probes a company homepage and extracts candidate Terms, Privacy, and User Agreement links.
    Enforces strict SSRF validation before attempting connection.
    """
    try:
        parsed = validate_url(base_url)
        resolve_and_verify_hostname(parsed.hostname)
    except URLValidationError as exc:
        logger.debug("Discovery URL validation rejected %s: %s", base_url, exc)
        return []

    candidates: List[Dict[str, str]] = []
    seen_urls: set[str] = set()

    try:
        async with httpx.AsyncClient(timeout=4.5, follow_redirects=True, verify=True) as client:
            resp = await client.get(base_url, headers=BROWSER_HEADERS)
            if resp.status_code != 200 or not resp.text:
                return []

            soup = BeautifulSoup(resp.text[:600000], "html.parser")
            target_keywords = [
                "terms", "privacy", "legal", "tos", "policy", "policies",
                "agreement", "disclaimer", "condition", "acceptable use",
                "cookie", "cookies", "security", "dpa", "data protection", "eula"
            ]

            # Collect candidate anchor tags prioritizing footers and navs
            all_links = []
            for container in soup.find_all(["footer", "nav", "div", "section"]):
                all_links.extend(container.find_all("a", href=True))
            if not all_links:
                all_links = soup.find_all("a", href=True)

            for a in all_links:
                href = a["href"].strip()
                if not href or href.startswith(("#", "javascript:", "mailto:", "tel:")):
                    continue

                text = a.get_text(separator=" ", strip=True)
                combined = f"{text} {href}".lower()

                if any(kw in combined for kw in target_keywords):
                    full_url = urljoin(str(resp.url), href)
                    # Strip URL fragments and tracking queries
                    parsed_full = urlparse(full_url)
                    clean_full_url = f"{parsed_full.scheme}://{parsed_full.netloc}{parsed_full.path}"
                    if parsed_full.query and not any(utm in parsed_full.query for utm in ("utm_", "ref", "source")):
                        clean_full_url = f"{clean_full_url}?{parsed_full.query}"

                    if clean_full_url.startswith(("http://", "https://")) and clean_full_url not in seen_urls:
                        # Validate full URL against SSRF
                        try:
                            p_target = validate_url(clean_full_url)
                            resolve_and_verify_hostname(p_target.hostname)
                        except URLValidationError:
                            continue

                        seen_urls.add(clean_full_url)
                        clean_title = _normalize_title(text, default_title="Legal Resource")
                        snippet = f"Discovered directly on official website ({parsed.hostname})"
                        candidates.append({
                            "title": clean_title,
                            "url": clean_full_url,
                            "snippet": snippet,
                            "source": "discovery",
                        })

                        if len(candidates) >= MAX_DISCOVERY_CANDIDATES:
                            break

    except Exception as exc:
        logger.debug("Crawl discovery exception for %s: %s", base_url, exc)

    return candidates


async def probe_canonical_endpoints(base_url: str, seen_urls: set[str]) -> List[Dict[str, str]]:
    """
    Directly probes standard canonical policy endpoints on the target host (e.g. /terms, /privacy).
    Useful for modern client-rendered single page applications (SPAs) where footers aren't in static HTML.
    """
    discovered: List[Dict[str, str]] = []
    try:
        parsed = validate_url(base_url)
        resolve_and_verify_hostname(parsed.hostname)
    except URLValidationError:
        return []

    host_root = f"{parsed.scheme}://{parsed.netloc}"

    try:
        async with httpx.AsyncClient(timeout=3.0, follow_redirects=True, verify=True) as client:
            for path, default_title in CANONICAL_LEGAL_PATHS:
                target_url = urljoin(host_root, path)
                if target_url in seen_urls:
                    continue

                try:
                    p_target = validate_url(target_url)
                    resolve_and_verify_hostname(p_target.hostname)
                except URLValidationError:
                    continue

                try:
                    resp = await client.get(target_url, headers=BROWSER_HEADERS)
                    # Successful response containing HTML and legal terms
                    if resp.status_code == 200 and "text/html" in resp.headers.get("content-type", ""):
                        text_sample = resp.text[:10000].lower()
                        # Verify the page actually contains policy text rather than a soft-404 homepage
                        if any(kw in text_sample for kw in ("terms", "privacy", "agreement", "conditions", "policy", "governs")):
                            clean_url = str(resp.url)
                            if clean_url not in seen_urls:
                                seen_urls.add(clean_url)
                                discovered.append({
                                    "title": f"{parsed.netloc.replace('www.', '').capitalize()} {default_title}",
                                    "url": clean_url,
                                    "snippet": f"Verified official legal endpoint on {parsed.hostname}",
                                    "source": "auto_probe",
                                })
                except Exception:
                    continue

                if len(discovered) >= 6:
                    break
    except Exception as exc:
        logger.debug("Canonical probing error for %s: %s", base_url, exc)

    return discovered


async def search_engine_fallback(query: str, seen_urls: set[str]) -> List[Dict[str, str]]:
    """
    Fallback web search using privacy-preserving HTML search engine endpoints
    to find official policy pages when direct domain resolution misses.
    """
    discovered: List[Dict[str, str]] = []
    clean_q = re.sub(r"[^a-zA-Z0-9\s\.\-]", "", query).strip()
    if not clean_q:
        return []

    search_urls = [
        f"https://html.duckduckgo.com/html/?q={clean_q}+terms+of+service+privacy+policy",
    ]

    try:
        async with httpx.AsyncClient(timeout=4.0, follow_redirects=True, verify=True) as client:
            for s_url in search_urls:
                try:
                    p_s = validate_url(s_url)
                    resolve_and_verify_hostname(p_s.hostname)
                except URLValidationError:
                    continue

                resp = await client.get(s_url, headers=BROWSER_HEADERS)
                if resp.status_code != 200 or not resp.text:
                    continue

                soup = BeautifulSoup(resp.text[:400000], "html.parser")
                # DuckDuckGo HTML results use .result__url or a.result__snippet
                for a in soup.find_all("a", href=True):
                    href = a["href"]
                    # Handle DDG redirect wrappers
                    if "uddg=" in href:
                        import urllib.parse
                        match = re.search(r"uddg=([^&]+)", href)
                        if match:
                            href = urllib.parse.unquote(match.group(1))

                    if not href.startswith(("http://", "https://")):
                        continue

                    combined = f"{a.get_text()} {href}".lower()
                    if any(kw in combined for kw in ("terms", "privacy", "tos", "policy", "legal")):
                        try:
                            p_target = validate_url(href)
                            resolve_and_verify_hostname(p_target.hostname)
                        except URLValidationError:
                            continue

                        # Avoid search engines, ads, or aggregators
                        if any(agg in p_target.netloc for agg in ("duckduckgo.com", "google.com", "bing.com", "yahoo.com", "youtube.com")):
                            continue

                        if href not in seen_urls:
                            seen_urls.add(href)
                            title_text = _normalize_title(a.get_text(), default_title="Official Legal Policy")
                            discovered.append({
                                "title": title_text,
                                "url": href,
                                "snippet": f"Discovered via search for {clean_q} ({p_target.hostname})",
                                "source": "search_discovery",
                            })

                        if len(discovered) >= 4:
                            break

                if discovered:
                    break
    except Exception as exc:
        logger.debug("Search engine fallback exception for query '%s': %s", query, exc)

    return discovered


async def discover_policy_urls(query: str, max_candidates: int = MAX_DISCOVERY_CANDIDATES) -> Dict[str, Any]:
    """
    Discover candidate official Terms of Service, Privacy Policy, and User Agreement URLs for a company.
    1. Checks in-memory cache.
    2. Searches the authoritative known directory (covering 249+ major companies with 501+ verified documents).
    3. If unknown or insufficient candidates found: dynamically auto-finds policies via:
       - Multi-TLD domain guessing & homepage DOM crawling.
       - Direct canonical legal path probing (/terms, /privacy).
       - Live search engine fallback.
    4. Prioritizes, deduplicates, and restricts the results up to max_candidates.
    """
    clean_q = query.strip().lower()
    if not clean_q:
        return {"candidates": [], "cached": False, "total": 0}

    # 1. Check in-memory cache
    if clean_q in _query_cache:
        cached_candidates, _ = _query_cache[clean_q]
        return {
            "candidates": cached_candidates[:max_candidates],
            "cached": True,
            "total": len(cached_candidates),
        }

    candidates: List[Dict[str, str]] = []
    seen_urls: set[str] = set()

    # 2. Check authoritative known directory
    known_results = search_known_directory(clean_q)
    for item in known_results:
        if item["url"] not in seen_urls:
            seen_urls.add(item["url"])
            candidates.append(item)

    # 3. Dynamic Auto-Find if not found in directory or fewer than 2 candidates
    if len(candidates) < 2:
        probe_urls: List[str] = []

        # Determine target base URLs
        if clean_q.startswith(("http://", "https://")):
            probe_urls.append(clean_q)
        elif "." in clean_q and not " " in clean_q:
            probe_urls.extend([f"https://{clean_q}", f"https://www.{clean_q}"])
        else:
            clean_domain = re.sub(r"[^a-z0-9\-]", "", clean_q)
            if clean_domain:
                # Probe likely web domains across popular top-level domains
                tlds = ["com", "io", "ai", "app", "org", "co", "dev", "net", "so"]
                for tld in tlds:
                    probe_urls.append(f"https://{clean_domain}.{tld}")
                probe_urls.insert(0, f"https://www.{clean_domain}.com")

        # Step 3A: Direct homepage DOM crawl
        responsive_base_url: Optional[str] = None
        for target in probe_urls:
            discovered = await crawl_homepage_for_policy_links(target)
            if discovered:
                responsive_base_url = target
                for d in discovered:
                    if d["url"] not in seen_urls:
                        seen_urls.add(d["url"])
                        candidates.append(d)
            if len(candidates) >= 4:
                break

        # Step 3B: Canonical legal endpoint probing if responsive base URL was found
        if responsive_base_url:
            canonical_discovered = await probe_canonical_endpoints(responsive_base_url, seen_urls)
            for d in canonical_discovered:
                if d["url"] not in seen_urls:
                    seen_urls.add(d["url"])
                    candidates.append(d)

        # Step 3C: Search engine fallback if candidates are still sparse
        if len(candidates) < 2:
            search_discovered = await search_engine_fallback(clean_q, seen_urls)
            for d in search_discovered:
                if d["url"] not in seen_urls:
                    seen_urls.add(d["url"])
                    candidates.append(d)

    # Prioritize and order policies (Terms -> Privacy -> Cookies / Other)
    ordered_candidates = _prioritize_policies(candidates)
    restricted_candidates = ordered_candidates[:max_candidates]

    # Cache result
    _query_cache[clean_q] = (restricted_candidates, datetime.now(timezone.utc))

    return {
        "candidates": restricted_candidates,
        "cached": False,
        "total": len(restricted_candidates),
    }
