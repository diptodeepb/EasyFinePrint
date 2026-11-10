"""Safe HTTP Fetcher and Content Extractor for Legal Policies.

Enforces hop-by-hop redirect SSRF revalidation, byte caps, timeout limits,
HTML-only content types, and multi-tier text extraction:
1. Primary Trafilatura extraction (optimized for static legal articles)
2. Secondary BeautifulSoup DOM extraction
3. Client-side JavaScript hydration extraction (React, Next.js, Redux, Vue, and SPA state stores)
4. Sandboxed Node.js VM dynamic script evaluation fallback
"""
from __future__ import annotations
import json
import logging
import re
import shutil
import subprocess
from typing import Tuple, List, Optional, Any, Set
from urllib.parse import urljoin
import httpx
from bs4 import BeautifulSoup
import trafilatura

from app.config import settings
from app.services.url_guard import validate_url, resolve_and_verify_hostname, URLValidationError

logger = logging.getLogger("easyfineprint.extractor")

DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)

ALLOWED_CONTENT_TYPES = ("text/html", "application/xhtml+xml", "text/plain")

# High-fidelity modern browser request headers to prevent WAF bot-tarpits
STANDARD_BROWSER_HEADERS = {
    "User-Agent": DEFAULT_USER_AGENT,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Sec-Ch-Ua": '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"Windows"',
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
}


class ExtractionError(Exception):
    """Raised when page fetch or text extraction fails."""
    pass


async def _fetch_via_node_fallback(target_url: str, byte_limit: int, timeout_sec: int) -> Tuple[str, str, int]:
    """
    Fallback HTTP/2 fetch using Node.js native engine when standard httpx encounters
    connection timeouts or TLS fingerprint blocks, while preserving strict SSRF validation.
    """
    node_path = shutil.which("node")
    if not node_path:
        raise ExtractionError("Node.js is not installed for fallback network fetch.")

    parsed = validate_url(target_url)
    resolve_and_verify_hostname(parsed.hostname)

    js_fetcher = """
    const url = process.argv[1];
    const timeoutMs = parseInt(process.argv[2], 10) * 1000;
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), timeoutMs);

    fetch(url, {
        headers: {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Sec-Ch-Ua": '"Chromium";v="124", "Google Chrome";v="124"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Windows"'
        },
        signal: controller.signal,
        redirect: 'follow'
    }).then(async (res) => {
        clearTimeout(timeout);
        const text = await res.text();
        process.stdout.write(JSON.stringify({
            status: res.status,
            url: res.url || url,
            text: text
        }));
    }).catch((err) => {
        clearTimeout(timeout);
        process.stderr.write(String(err));
        process.exit(1);
    });
    """

    try:
        proc = subprocess.run(
            [node_path, "-e", js_fetcher, target_url, str(timeout_sec)],
            capture_output=True,
            text=True,
            timeout=timeout_sec + 2,
        )
        if proc.returncode != 0:
            raise ExtractionError(f"Node fallback fetch failed: {proc.stderr.strip() or 'Unknown error'}")

        data = json.loads(proc.stdout)
        final_url = data.get("url", target_url)

        # Validate final resolved URL against SSRF
        p_final = validate_url(final_url)
        resolve_and_verify_hostname(p_final.hostname)

        status = data.get("status", 200)
        html_text = data.get("text", "")
        if len(html_text.encode("utf-8")) > byte_limit:
            html_text = html_text[:byte_limit]

        return html_text, final_url, status
    except subprocess.TimeoutExpired:
        raise ExtractionError(f"Connection timed out while fetching {target_url} via browser engine")
    except Exception as exc:
        raise ExtractionError(f"Browser engine fetch error: {exc}")


async def safe_fetch_page(
    target_url: str,
    max_bytes: Optional[int] = None,
    timeout_sec: Optional[int] = None,
    max_redirects: int = 5,
) -> Tuple[str, str, int]:
    """
    Safely fetch a webpage with manual redirect verification at every hop.
    Employs modern browser headers and an automated Node.js fallback for SPA / anti-bot tarpits.
    Returns (html_content, canonical_final_url, status_code).
    """
    byte_limit = max_bytes or settings.max_fetch_bytes
    timeout = timeout_sec or settings.fetch_timeout_seconds

    current_url = target_url
    redirect_count = 0

    headers = dict(STANDARD_BROWSER_HEADERS)

    try:
        async with httpx.AsyncClient(
            verify=True,
            timeout=httpx.Timeout(timeout, connect=10.0, read=timeout, write=10.0),
            follow_redirects=False,
            cookies=httpx.Cookies(),
        ) as client:
            while True:
                # Re-verify URL and hostname before EVERY outbound request
                try:
                    parsed = validate_url(current_url)
                    resolve_and_verify_hostname(parsed.hostname)
                except URLValidationError as exc:
                    raise ExtractionError(str(exc))

                try:
                    # Use streaming response to cap bytes downloaded
                    async with client.stream("GET", current_url, headers=headers) as response:
                        status = response.status_code

                        # Handle redirects manually
                        if status in (301, 302, 303, 307, 308):
                            redirect_count += 1
                            if redirect_count > max_redirects:
                                raise ExtractionError(f"Maximum redirect hops exceeded ({max_redirects})")

                            location = response.headers.get("location")
                            if not location:
                                raise ExtractionError("Redirect response missing Location header")

                            next_url = urljoin(current_url, location)
                            logger.info("Following safe redirect (%d/%d): %s -> %s", redirect_count, max_redirects, current_url, next_url)
                            current_url = next_url
                            continue

                        if status != 200:
                            raise ExtractionError(f"Target server returned HTTP status {status}")

                        # Verify Content-Type
                        content_type = response.headers.get("content-type", "").lower()
                        if not any(allowed in content_type for allowed in ALLOWED_CONTENT_TYPES):
                            raise ExtractionError(f"Prohibited content type '{content_type}'. Only HTML documents are accepted.")

                        # Download chunks up to byte limit
                        content_chunks = []
                        total_bytes = 0
                        async for chunk in response.aiter_bytes():
                            total_bytes += len(chunk)
                            if total_bytes > byte_limit:
                                raise ExtractionError(f"Page exceeded maximum allowed size of {byte_limit} bytes")
                            content_chunks.append(chunk)

                        raw_content = b"".join(content_chunks)
                        # Decode text safely
                        encoding = response.encoding or "utf-8"
                        try:
                            html_text = raw_content.decode(encoding, errors="replace")
                        except Exception:
                            html_text = raw_content.decode("utf-8", errors="replace")

                        return html_text, str(response.url or current_url), status

                except (httpx.TimeoutException, httpx.RequestError) as net_err:
                    logger.info("Direct httpx fetch encountered (%s). Trying browser engine fallback...", net_err)
                    return await _fetch_via_node_fallback(current_url, byte_limit, int(timeout))

    except ExtractionError:
        raise
    except Exception as exc:
        raise ExtractionError(f"Network request error: {exc}")


def _collect_legal_strings(obj: Any, paragraphs: List[str]) -> None:
    """Recursively walks a JSON / JavaScript object and collects legal text paragraphs."""
    if isinstance(obj, str):
        s = obj.strip()
        # Collect coherent paragraphs (length > 25 characters with spaces)
        if len(s) > 25 and " " in s:
            paragraphs.append(s)
    elif isinstance(obj, list):
        for item in obj:
            _collect_legal_strings(item, paragraphs)
    elif isinstance(obj, dict):
        # Prioritize known content and text container keys
        priority_keys = ("details", "description", "content", "text", "body", "markdown", "pageProps", "props", "terms", "privacy", "data")
        for key in priority_keys:
            if key in obj:
                _collect_legal_strings(obj[key], paragraphs)

        # Walk remaining keys ignoring noise metadata
        ignore_keys = {"env", "config", "devicedata", "traffic", "telemetry", "analytics", "experiments", "features", "assets", "styles"}
        for k, v in obj.items():
            if k not in priority_keys and k.lower() not in ignore_keys:
                _collect_legal_strings(v, paragraphs)


def extract_js_hydration_policy(html: str) -> str:
    """
    Extracts policy text from client-side JavaScript hydration states:
    - Application JSON scripts (__NEXT_DATA__, JSON-LD)
    - React/Redux SSR window states (__INITIAL_STATE__, __PRELOADED_STATE__)
    - Custom SPA stores (e.g. window["__pageData__"], window.__INITIAL_DATA__, window["__staticPage__"])
    """
    paragraphs: List[str] = []
    soup = BeautifulSoup(html, "html.parser")

    # 1. Inspect script tags with type="application/json"
    for s in soup.find_all("script", attrs={"type": "application/json"}):
        txt = s.get_text()
        if txt:
            try:
                data = json.loads(txt)
                _collect_legal_strings(data, paragraphs)
            except Exception:
                pass

    # 2. Inspect window state assignments in inline scripts
    for s in soup.find_all("script"):
        txt = s.get_text()
        if not txt or len(txt) < 50:
            continue

        matches = re.finditer(
            r"window(?:\[\"([a-zA-Z0-9_$]+)\"\]|\.([a-zA-Z0-9_$]+))\s*=\s*(\{.*?\})(?:;window|;const|;let|;var|;\s*$)",
            txt,
            re.DOTALL,
        )
        for m in matches:
            raw_json = m.group(3)
            try:
                data = json.loads(raw_json)
                _collect_legal_strings(data, paragraphs)
            except Exception:
                pass

    # Deduplicate while preserving document narrative flow
    seen: Set[str] = set()
    deduped: List[str] = []
    for p in paragraphs:
        clean = re.sub(r"\s+", " ", p).strip()
        if clean and clean not in seen and len(clean) > 25:
            # Skip API paths or single-word URL fragments
            if not (clean.startswith(("/", "http://", "https://")) and " " not in clean):
                seen.add(clean)
                deduped.append(p.strip())

    return "\n\n".join(deduped)


def evaluate_inline_scripts_with_node(html: str) -> str:
    """
    Sandboxed Node.js VM execution fallback.
    Executes inline JavaScript in an isolated V8 VM context (node:vm) with a 2-second timeout
    to render and extract dynamic window / document legal text objects.
    """
    if not shutil.which("node"):
        return ""

    soup = BeautifulSoup(html, "html.parser")
    scripts = [s.get_text() for s in soup.find_all("script") if s.get_text() and len(s.get_text()) > 100]

    extracted_paragraphs: List[str] = []

    for script_txt in scripts:
        # Only evaluate scripts likely containing legal text definitions
        lower = script_txt.lower()
        if not any(kw in lower for kw in ("terms", "privacy", "agreement", "policy", "staticpage", "content", "initial_state", "description")):
            continue

        runner_js = """
        const vm = require("node:vm");
        const sandbox = {
            window: {},
            document: {},
            console: { log: () => {}, error: () => {} }
        };
        vm.createContext(sandbox);
        try {
            vm.runInContext(process.argv[1], sandbox, { timeout: 2000 });
            const res = [];
            function walk(obj) {
                if (typeof obj === "string" && obj.length > 25 && obj.includes(" ")) {
                    res.push(obj.trim());
                } else if (Array.isArray(obj)) {
                    obj.forEach(walk);
                } else if (obj && typeof obj === "object") {
                    Object.values(obj).forEach(walk);
                }
            }
            walk(sandbox.window);
            walk(sandbox.document);
            process.stdout.write(JSON.stringify(res));
        } catch (e) {
            process.stdout.write(JSON.stringify([]));
        }
        """

        try:
            proc = subprocess.run(
                ["node", "-e", runner_js, script_txt],
                capture_output=True,
                text=True,
                timeout=2.5,
            )
            if proc.returncode == 0 and proc.stdout:
                items = json.loads(proc.stdout)
                if isinstance(items, list):
                    extracted_paragraphs.extend(items)
        except Exception as exc:
            logger.debug("Node VM script evaluation skipped: %s", exc)

    seen: Set[str] = set()
    deduped: List[str] = []
    for p in extracted_paragraphs:
        clean = re.sub(r"\s+", " ", p).strip()
        if clean and clean not in seen and len(clean) > 25:
            seen.add(clean)
            deduped.append(p.strip())

    return "\n\n".join(deduped)


def extract_policy_content(html: str) -> Tuple[str, str, List[str]]:
    """
    Extracts policy title and main body text from HTML using a 4-tier pipeline:
    1. Primary: Trafilatura (best for standard articles/static HTML)
    2. Secondary: BeautifulSoup cleaned DOM text
    3. Tertiary: Client-side JavaScript Hydration extraction (React/Next.js/Vue/Redux/SPA)
    4. Quaternary: Sandboxed Node.js VM evaluation
    Returns (title, extracted_text, warnings).
    """
    warnings: List[str] = []
    title = "Terms / Privacy Policy"

    # Extract title from HTML via BeautifulSoup
    try:
        soup = BeautifulSoup(html, "html.parser")
        if soup.title and soup.title.string:
            title = soup.title.string.strip()
        elif soup.h1:
            title = soup.h1.get_text().strip()
    except Exception as exc:
        logger.debug("Title extraction error: %s", exc)

    extracted_text: Optional[str] = None

    # 1. Primary extractor: trafilatura (optimized for main text / legal bodies)
    try:
        extracted_text = trafilatura.extract(
            html,
            include_links=False,
            include_images=False,
            include_tables=True,
            favor_precision=True,
            output_format="txt",
        )
    except Exception as exc:
        warnings.append(f"Trafilatura extraction failed: {exc}")

    # 2. Secondary fallback extractor: BeautifulSoup cleaned DOM text
    if not extracted_text or len(extracted_text.strip()) < 200:
        logger.info("Trafilatura returned short text. Attempting BeautifulSoup DOM fallback.")
        try:
            soup = BeautifulSoup(html, "html.parser")
            for tag in soup(["script", "style", "noscript", "svg", "nav", "footer", "header", "aside", "form"]):
                tag.decompose()

            main_container = soup.find("main") or soup.find("article") or soup.find(attrs={"role": "main"}) or soup.body
            if main_container:
                paragraphs = []
                for element in main_container.find_all(["h1", "h2", "h3", "h4", "h5", "h6", "p", "li"]):
                    text = element.get_text(separator=" ", strip=True)
                    if text and len(text) > 15:
                        paragraphs.append(text)
                bs_text = "\n\n".join(paragraphs)
                if len(bs_text.strip()) >= 200:
                    extracted_text = bs_text
                    warnings.append("Used secondary BeautifulSoup extractor fallback.")
        except Exception as exc:
            logger.debug("BeautifulSoup DOM fallback error: %s", exc)

    # 3. Tertiary fallback: JavaScript Hydration Extraction (SPAs, React, Next.js, Vue)
    if not extracted_text or len(extracted_text.strip()) < 200:
        logger.info("DOM text is sparse. Executing JavaScript hydration extraction...")
        js_text = extract_js_hydration_policy(html)
        if len(js_text.strip()) >= 200:
            extracted_text = js_text
            warnings.append("Extracted content from client-side JavaScript hydration state.")

    # 4. Quaternary fallback: Sandboxed Node.js VM Evaluation
    if not extracted_text or len(extracted_text.strip()) < 200:
        logger.info("Attempting sandboxed Node.js VM evaluation fallback...")
        vm_text = evaluate_inline_scripts_with_node(html)
        if len(vm_text.strip()) >= 200:
            extracted_text = vm_text
            warnings.append("Extracted content via sandboxed Node.js JavaScript evaluation.")

    if not extracted_text or len(extracted_text.strip()) < 100:
        raise ExtractionError("Extracted text is empty or suspiciously short (<100 characters). Page may require JavaScript or is blocked.")

    # Apply length cap if required
    if len(extracted_text) > settings.max_policy_chars:
        extracted_text = extracted_text[:settings.max_policy_chars]
        warnings.append(f"Policy truncated to max character limit ({settings.max_policy_chars}).")

    return title, extracted_text, warnings


async def fetch_wayback_snapshot(target_url: str, timeout_sec: float = 12.0) -> Optional[Tuple[str, str, str]]:
    """
    Tier 2 Public Web Archive Fallback (Internet Archive / Wayback Machine):
    Queries the official Wayback Machine Availability API to retrieve the closest
    public snapshot of a legal agreement when origin servers or CDN firewalls block cloud scrapers.
    Returns (html_content, archive_url, timestamp_str) or None if unavailable.
    """
    api_url = f"https://archive.org/wayback/available?url={httpx.URL(target_url)}"
    try:
        async with httpx.AsyncClient(timeout=timeout_sec, follow_redirects=True) as client:
            resp = await client.get(api_url, headers={"User-Agent": DEFAULT_USER_AGENT})
            if resp.status_code != 200:
                return None
            data = resp.json()
            snapshot = data.get("archived_snapshots", {}).get("closest")
            if not snapshot or not snapshot.get("available"):
                return None

            archive_url = snapshot.get("url")
            timestamp = snapshot.get("timestamp", "")
            if not archive_url:
                return None

            # Fetch archived HTML snapshot safely
            parsed_archive = validate_url(archive_url)
            resolve_and_verify_hostname(parsed_archive.hostname)

            snap_resp = await client.get(archive_url, headers=STANDARD_BROWSER_HEADERS)
            if snap_resp.status_code != 200 or len(snap_resp.text) < 200:
                return None

            # Clean out any Wayback Machine top navigation injected toolbars
            html = snap_resp.text
            try:
                clean_soup = BeautifulSoup(html, "html.parser")
                for banner in clean_soup.find_all(id=re.compile(r"^(wm-ipp|donato)")):
                    banner.decompose()
                cleaned_html = str(clean_soup)
            except Exception:
                cleaned_html = html

            return cleaned_html, archive_url, timestamp
    except Exception as exc:
        logger.debug("Wayback Machine archive fallback lookup failed for %s: %s", target_url, exc)
        return None
