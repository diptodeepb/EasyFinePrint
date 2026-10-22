"""Evidence and Citation Validation Service.

Validates that every claim and finding returned by the AI is backed by an exact,
verbatim quote from the corresponding snapshot text. Drops unsupported findings.
"""
from __future__ import annotations
import logging
import re
from typing import List, Tuple, Dict, Any, Optional
from app.services.normalizer import normalize_policy_text

logger = logging.getLogger("easyfineprint.validator")

VALID_CATEGORIES = {
    "renewal",
    "cancellation",
    "data",
    "price_change",
    "disputes",
    "liability",
    "termination",
    "safety",
    "other",
}

VALID_SEVERITIES = {"low", "medium", "high", "uncertain"}
MIN_EXCERPT_LENGTH = 15  # Minimum characters for a non-trivial quote


def normalize_for_quote_search(text: str) -> str:
    """Standardize whitespace and punctuation for resilient quote matching."""
    if not text:
        return ""
    # Standardize whitespace to single space and lowercase for search
    text = re.sub(r"\s+", " ", text).strip().lower()
    # Normalize fancy quotes and apostrophes
    text = text.replace("“", '"').replace("”", '"').replace("’", "'").replace("‘", "'")
    return text


def verify_quote_in_text(quote: str, source_text: str) -> bool:
    """
    Check if verbatim quote exists in the source text.
    Handles slight punctuation/whitespace variations safely.
    """
    if not quote or not source_text:
        return False

    clean_quote = normalize_for_quote_search(quote)
    if len(clean_quote) < MIN_EXCERPT_LENGTH:
        return False

    clean_source = normalize_for_quote_search(source_text)
    return clean_quote in clean_source


def _safe_str(val: Any) -> str:
    if val is None:
        return ""
    return str(val).strip()


def validate_initial_findings(findings: List[Dict[str, Any]], source_text: str) -> Tuple[List[Dict[str, Any]], str]:
    """
    Validate findings from initial policy analysis against the snapshot text.
    Returns (validated_findings, validation_status: 'passed' | 'partial' | 'failed').
    """
    if not findings:
        return [], "passed"

    validated: List[Dict[str, Any]] = []
    dropped_count = 0

    for item in findings:
        excerpt = _safe_str(item.get("exact_excerpt"))
        category = _safe_str(item.get("category", "other")).lower()
        severity = _safe_str(item.get("severity", "uncertain")).lower()

        # 1. Category and severity validation
        if category not in VALID_CATEGORIES:
            category = "other"
        if severity not in VALID_SEVERITIES:
            severity = "uncertain"

        # 2. Quote verification against actual source text
        is_valid_quote = verify_quote_in_text(excerpt, source_text)

        if is_valid_quote:
            validated.append({
                "category": category,
                "severity": severity,
                "exact_excerpt": excerpt,
                "explanation": _safe_str(item.get("explanation")),
                "why_it_might_matter": _safe_str(item.get("why_it_might_matter")),
                "uncertainty": _safe_str(item.get("uncertainty")) or None,
            })
        else:
            dropped_count += 1
            logger.warning("Dropped finding with unverified quotation: '%s...'", excerpt[:60])

    if not validated and findings:
        return [], "failed"
    elif dropped_count > 0:
        return validated, "partial"
    else:
        return validated, "passed"


def validate_change_explanations(
    ai_changes: List[Dict[str, Any]],
    deterministic_diffs: List[Dict[str, Any]],
    old_text: str,
    new_text: str,
) -> Tuple[List[Dict[str, Any]], str]:
    """
    Correlate AI-explained changes with deterministic diff blocks and validate quotes.
    Returns (validated_diff_items, validation_status).
    """
    diff_map = {d["change_id"]: dict(d) for d in deterministic_diffs}
    validated_count = 0
    total_ai_changes = len(ai_changes)

    for item in ai_changes:
        cid = item.get("change_id")
        if cid not in diff_map:
            continue

        excerpt = item.get("exact_excerpt")
        src_version = (item.get("source_version") or "new").lower()
        significance = (item.get("significance") or "uncertain").lower()

        if significance not in VALID_SEVERITIES:
            significance = "uncertain"

        target_text = new_text if src_version == "new" else old_text
        quote_valid = verify_quote_in_text(excerpt, target_text) if excerpt else False

        diff_map[cid]["explanation"] = _safe_str(item.get("explanation"))
        diff_map[cid]["possible_implication"] = _safe_str(item.get("possible_implication"))
        diff_map[cid]["uncertainty"] = _safe_str(item.get("uncertainty")) or None
        diff_map[cid]["significance"] = significance

        if quote_valid and excerpt:
            diff_map[cid]["exact_excerpt"] = excerpt
            diff_map[cid]["source_version"] = src_version
            validated_count += 1
        else:
            diff_map[cid]["exact_excerpt"] = None
            diff_map[cid]["source_version"] = None

    result_changes = list(diff_map.values())

    if total_ai_changes == 0:
        return result_changes, "skipped"
    elif validated_count == total_ai_changes:
        return result_changes, "passed"
    elif validated_count > 0:
        return result_changes, "partial"
    else:
        return result_changes, "failed"
