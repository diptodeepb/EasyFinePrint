"""Text Normalization and Content Hashing for Deterministic Policy Versioning."""
from __future__ import annotations
import hashlib
import re
import unicodedata


def normalize_policy_text(text: str) -> str:
    """
    Standardize text formatting while strictly preserving legal semantics, numbers,
    punctuation, capitalization, and paragraph boundaries.

    Rules:
    1. Unicode NFKC normalization.
    2. Convert all line endings to \\n.
    3. Collapse multiple spaces and horizontal tabs within each line.
    4. Strip whitespace from line ends.
    5. Standardize paragraph breaks: collapse 3+ consecutive newlines to 2.
    """
    if not text:
        return ""

    # 1. Unicode NFKC normalization (standardizes characters, ligature accents, quotes)
    normalized = unicodedata.normalize("NFKC", text)

    # 2. Standardize carriage returns
    normalized = normalized.replace("\r\n", "\n").replace("\r", "\n")

    # 3. Clean up lines
    lines = normalized.split("\n")
    cleaned_lines = []
    for line in lines:
        # Collapse multiple inline spaces and tabs into single space
        line = re.sub(r"[ \t]+", " ", line).strip()
        cleaned_lines.append(line)

    result = "\n".join(cleaned_lines)

    # 4. Standardize paragraph boundaries (max 2 consecutive newlines)
    result = re.sub(r"\n{3,}", "\n\n", result)

    return result.strip()


def compute_content_hash(text: str) -> str:
    """Compute deterministic SHA-256 hash of normalized text."""
    normalized = normalize_policy_text(text)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def canonicalize_url(url: str) -> str:
    """Normalize a URL to its canonical form for duplicate detection.
    
    Strips trailing slashes, default ports, www prefixes, query params, fragments,
    and normalizes scheme, hostname, and path to lowercase.
    """
    if not url:
        return ""
    clean = url.strip()
    if clean.startswith("/"):
        clean_path = re.sub(r"/+", "/", clean).rstrip("/")
        return clean_path.lower() if clean_path else "/"

    if not (clean.startswith("http://") or clean.startswith("https://")):
        clean = "https://" + clean

    try:
        from urllib.parse import urlparse
        parsed = urlparse(clean)
        scheme = "https"
        host = (parsed.netloc or "").lower()
        if host.endswith(":443"):
            host = host[:-4]
        elif host.endswith(":80"):
            host = host[:-3]
        if host.startswith("www."):
            host = host[4:]

        path = re.sub(r"/+", "/", parsed.path or "/").rstrip("/")
        path = path.lower()
        if not path:
            path = "/"
        return f"{scheme}://{host}{path}"
    except Exception:
        return clean.lower().rstrip("/")
