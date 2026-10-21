"""Safe HTTP Fetcher and Content Extractor for Legal Policies.

Enforces hop-by-hop redirect SSRF revalidation, byte caps, timeout limits,
HTML-only content types, and robust main text extraction (trafilatura + BeautifulSoup fallback).
"""
from __future__ import annotations
import logging
from typing import Tuple, List, Optional
from urllib.parse import urljoin
import httpx
from bs4 import BeautifulSoup
import trafilatura

from app.config import settings
from app.services.url_guard import validate_url, resolve_and_verify_hostname, URLValidationError

logger = logging.getLogger("easyfineprint.extractor")

DEFAULT_USER_AGENT = "EasyFinePrint/1.0 (+https://github.com/diptodeepb/EasyFinePrint; Policy-Monitor-Bot)"
ALLOWED_CONTENT_TYPES = ("text/html", "application/xhtml+xml", "text/plain")


class ExtractionError(Exception):
    """Raised when page fetch or text extraction fails."""
    pass


async def safe_fetch_page(
    target_url: str,
    max_bytes: Optional[int] = None,
    timeout_sec: Optional[int] = None,
    max_redirects: int = 5,
) -> Tuple[str, str, int]:
    """
    Safely fetch a webpage with manual redirect verification at every hop.
    Returns (html_content, canonical_final_url, status_code).
    """
    byte_limit = max_bytes or settings.max_fetch_bytes
    timeout = timeout_sec or settings.fetch_timeout_seconds

    current_url = target_url
    redirect_count = 0

    headers = {
        "User-Agent": DEFAULT_USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }

    async with httpx.AsyncClient(
        verify=True,
        timeout=httpx.Timeout(timeout, connect=timeout / 2),
        follow_redirects=False,
    ) as client:
        while True:
            # Re-verify URL and hostname before EVERY outbound request
            try:
                parsed = validate_url(current_url)
                resolve_and_verify_hostname(parsed.hostname)
            except URLValidationError as exc:
                raise ExtractionError(f"URL validation failed for {current_url}: {exc}")

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

            except httpx.TimeoutException:
                raise ExtractionError(f"Connection timed out while fetching {current_url}")
            except httpx.RequestError as exc:
                raise ExtractionError(f"Network request error: {exc}")


def extract_policy_content(html: str) -> Tuple[str, str, List[str]]:
    """
    Extracts policy title and main body text from HTML.
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

    # 1. Primary extractor: trafilatura (optimized for main text / legal bodies)
    extracted_text: Optional[str] = None
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

    # 2. Fallback extractor: BeautifulSoup cleaned DOM text
    if not extracted_text or len(extracted_text.strip()) < 200:
        logger.info("Trafilatura returned empty or short text. Falling back to BeautifulSoup.")
        warnings.append("Used secondary BeautifulSoup extractor fallback.")
        try:
            soup = BeautifulSoup(html, "html.parser")
            # Remove scripts, styles, forms, navigation, footer chrome
            for tag in soup(["script", "style", "noscript", "svg", "nav", "footer", "header", "aside", "form"]):
                tag.decompose()

            # Prefer main, article or div[role=main] if present
            main_container = soup.find("main") or soup.find("article") or soup.find(attrs={"role": "main"}) or soup.body
            if main_container:
                paragraphs = []
                for element in main_container.find_all(["h1", "h2", "h3", "h4", "h5", "h6", "p", "li"]):
                    text = element.get_text(separator=" ", strip=True)
                    if text and len(text) > 15:
                        paragraphs.append(text)
                extracted_text = "\n\n".join(paragraphs)
            else:
                extracted_text = soup.get_text(separator="\n", strip=True)
        except Exception as exc:
            raise ExtractionError(f"HTML parsing and fallback extraction failed: {exc}")

    if not extracted_text or len(extracted_text.strip()) < 100:
        raise ExtractionError("Extracted text is empty or suspiciously short (<100 characters). Page may require JavaScript or is blocked.")

    # Apply length cap if required
    if len(extracted_text) > settings.max_policy_chars:
        extracted_text = extracted_text[:settings.max_policy_chars]
        warnings.append(f"Policy truncated to max character limit ({settings.max_policy_chars}).")

    return title, extracted_text, warnings
