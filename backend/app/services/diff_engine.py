"""Deterministic Diff Engine for Policy Text Comparison.

Splits normalized text by paragraphs and headings, runs difflib.SequenceMatcher,
and groups adjacent edits into auditable additions, removals, and modifications.
"""
from __future__ import annotations
import difflib
from typing import List, Dict, Any
from app.services.normalizer import normalize_policy_text, compute_content_hash


def split_into_paragraphs(text: str) -> List[str]:
    """Split text into non-empty logical paragraphs."""
    raw_paras = text.split("\n\n")
    return [p.strip() for p in raw_paras if p.strip()]


def compute_policy_diff(old_text: str, new_text: str) -> Dict[str, Any]:
    """
    Compute paragraph-level deterministic diff between two policy versions.
    Returns structured change items and statistical summary.
    """
    norm_old = normalize_policy_text(old_text)
    norm_new = normalize_policy_text(new_text)

    old_hash = compute_content_hash(norm_old)
    new_hash = compute_content_hash(norm_new)

    if old_hash == new_hash:
        return {
            "has_changes": False,
            "old_hash": old_hash,
            "new_hash": new_hash,
            "changes": [],
            "summary": {
                "total_changes": 0,
                "additions": 0,
                "removals": 0,
                "modifications": 0,
            },
        }

    old_paras = split_into_paragraphs(norm_old)
    new_paras = split_into_paragraphs(norm_new)

    matcher = difflib.SequenceMatcher(None, old_paras, new_paras)
    changes: List[Dict[str, Any]] = []
    change_idx = 1

    additions = 0
    removals = 0
    modifications = 0

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            continue

        old_chunk = "\n\n".join(old_paras[i1:i2]) if i1 < i2 else ""
        new_chunk = "\n\n".join(new_paras[j1:j2]) if j1 < j2 else ""

        if tag == "replace":
            change_type = "modification"
            modifications += 1
        elif tag == "delete":
            change_type = "removal"
            removals += 1
        elif tag == "insert":
            change_type = "addition"
            additions += 1
        else:
            continue

        changes.append({
            "change_id": f"diff_{change_idx}",
            "change_type": change_type,
            "old_text": old_chunk if old_chunk else None,
            "new_text": new_chunk if new_chunk else None,
            "old_range": [i1, i2],
            "new_range": [j1, j2],
        })
        change_idx += 1

    return {
        "has_changes": len(changes) > 0,
        "old_hash": old_hash,
        "new_hash": new_hash,
        "changes": changes,
        "summary": {
            "total_changes": len(changes),
            "additions": additions,
            "removals": removals,
            "modifications": modifications,
        },
    }


def prepare_bounded_diff_context(changes: List[Dict[str, Any]], max_chars: int = 15000) -> List[Dict[str, Any]]:
    """
    Format bounded diff context for AI explanation, preventing token overflows
    while preserving verbatim excerpts.
    """
    bounded_changes = []
    accumulated_chars = 0

    for chg in changes:
        old_txt = chg.get("old_text") or ""
        new_txt = chg.get("new_text") or ""

        # Truncate individual huge blocks if they exceed single block limit
        if len(old_txt) > 2000:
            old_txt = old_txt[:1000] + "\n... [TRUNCATED] ...\n" + old_txt[-1000:]
        if len(new_txt) > 2000:
            new_txt = new_txt[:1000] + "\n... [TRUNCATED] ...\n" + new_txt[-1000:]

        item_size = len(old_txt) + len(new_txt)
        if accumulated_chars + item_size > max_chars and bounded_changes:
            break

        bounded_changes.append({
            "change_id": chg["change_id"],
            "change_type": chg["change_type"],
            "old_text": old_txt if old_txt else None,
            "new_text": new_txt if new_txt else None,
        })
        accumulated_chars += item_size

    return bounded_changes
