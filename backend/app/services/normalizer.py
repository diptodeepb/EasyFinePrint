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
