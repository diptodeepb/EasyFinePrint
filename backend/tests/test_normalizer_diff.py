"""Tests for text normalization, SHA-256 hashing, and deterministic diffing."""
from app.services.normalizer import normalize_policy_text, compute_content_hash
from app.services.diff_engine import compute_policy_diff, split_into_paragraphs


def test_normalization_whitespace_and_newlines():
    raw_text = "Section 1.   Terms of Use.  \r\n\r\n\r\n\r\nParagraph 1 text here.\tExtra   spaces."
    norm = normalize_policy_text(raw_text)
    assert "\r" not in norm
    assert "Section 1. Terms of Use." in norm
    assert "Extra spaces." in norm
    assert "\n\n\n" not in norm


def test_identical_hash_for_formatting_changes():
    t1 = "1. Acceptance of Terms\n\nYou agree to these terms."
    t2 = "1.   Acceptance of Terms\r\n\r\n\r\nYou agree   to these terms.  "
    h1 = compute_content_hash(t1)
    h2 = compute_content_hash(t2)
    assert h1 == h2


def test_diff_identical_text_unchanged():
    text = "Clause A: All rights reserved.\n\nClause B: No warranties provided."
    diff = compute_policy_diff(text, text)
    assert diff["has_changes"] is False
    assert diff["summary"]["total_changes"] == 0
    assert len(diff["changes"]) == 0


def test_diff_clause_added():
    old_text = "Clause A: Standard terms apply."
    new_text = "Clause A: Standard terms apply.\n\nClause B: Subscriptions auto-renew every 30 days unless canceled."
    diff = compute_policy_diff(old_text, new_text)
    assert diff["has_changes"] is True
    assert diff["summary"]["additions"] == 1
    assert diff["summary"]["removals"] == 0
    change = diff["changes"][0]
    assert change["change_type"] == "addition"
    assert "auto-renew" in change["new_text"]
    assert change["old_text"] is None


def test_diff_clause_removed():
    old_text = "Clause 1: Account setup.\n\nClause 2: Cancellation allowed anytime via dashboard.\n\nClause 3: Contact."
    new_text = "Clause 1: Account setup.\n\nClause 3: Contact."
    diff = compute_policy_diff(old_text, new_text)
    assert diff["has_changes"] is True
    assert diff["summary"]["removals"] == 1
    change = diff["changes"][0]
    assert change["change_type"] == "removal"
    assert "Cancellation allowed" in change["old_text"]


def test_diff_clause_modified():
    old_text = "Liability Cap: In no event shall our liability exceed $500 total."
    new_text = "Liability Cap: In no event shall our liability exceed $10 total or the amount paid in the last 30 days."
    diff = compute_policy_diff(old_text, new_text)
    assert diff["has_changes"] is True
    assert diff["summary"]["modifications"] == 1
    change = diff["changes"][0]
    assert change["change_type"] == "modification"
    assert "$500" in change["old_text"]
    assert "$10" in change["new_text"]
