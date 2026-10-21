"""Policy Management, Extraction, Analysis, and Change Tracking Routes."""
from __future__ import annotations
import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from app.schemas.policy import (
    PolicyAnalyzeRequest,
    PolicyResponse,
    AnalysisResponse,
    SnapshotResponse,
    CheckResponse,
    CheckEventResponse,
    FindingSchema,
    DiffChangeSchema,
)
from app.services.extractor import safe_fetch_page, extract_policy_content, ExtractionError
from app.services.normalizer import normalize_policy_text, compute_content_hash
from app.services.diff_engine import compute_policy_diff
from app.services.gemma import analyze_policy_risk, explain_policy_changes
from app.db.repositories import repo

logger = logging.getLogger("easyfineprint.policies")
router = APIRouter(prefix="/policies", tags=["policies"])


def _format_analysis_response(analysis_doc: dict) -> AnalysisResponse:
    findings = [FindingSchema(**f) for f in analysis_doc.get("findings", [])]
    changes = [DiffChangeSchema(**c) for c in analysis_doc.get("changes", [])]
    return AnalysisResponse(
        id=analysis_doc["id"],
        policy_id=analysis_doc["policy_id"],
        analysis_type=analysis_doc["analysis_type"],
        old_snapshot_id=analysis_doc.get("old_snapshot_id"),
        new_snapshot_id=analysis_doc["new_snapshot_id"],
        summary=analysis_doc["summary"],
        findings=findings,
        changes=changes,
        model_id=analysis_doc["model_id"],
        created_at=analysis_doc["created_at"],
        validation_status=analysis_doc["validation_status"],
    )


@router.post("/analyze", response_model=PolicyResponse)
async def analyze_policy(req: PolicyAnalyzeRequest):
    """
    Analyze a public Terms of Service or Privacy Policy URL.
    Enforces SSRF guards, extracts text, stores baseline snapshot, and analyzes potential concerns.
    """
    raw_url = req.url.strip()
    try:
        html, canonical_url, status_code = await safe_fetch_page(raw_url)
    except ExtractionError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        logger.error("Unexpected fetch failure for %s: %s", raw_url, exc)
        raise HTTPException(status_code=500, detail=f"Failed to fetch policy page: {exc}")

    try:
        title, extracted_text, warnings = extract_policy_content(html)
    except ExtractionError as exc:
        raise HTTPException(status_code=422, detail=str(exc))

    normalized_text = normalize_policy_text(extracted_text)
    content_hash = compute_content_hash(normalized_text)

    # Check if policy already exists
    policy = await repo.get_policy_by_url(canonical_url)
    if not policy:
        policy = await repo.create_policy(url=raw_url, canonical_url=canonical_url, title=title)
        is_new_policy = True
    else:
        is_new_policy = False

    latest_snap = await repo.get_snapshot_by_id(policy.get("latest_snapshot_id", "")) if policy.get("latest_snapshot_id") else None

    # If already tracked and content is identical
    if latest_snap and latest_snap.get("content_hash") == content_hash:
        await repo.record_check_event(
            policy_id=policy["id"],
            status="unchanged",
            message="No textual changes detected compared to existing baseline.",
            old_snapshot_id=latest_snap["id"],
            new_snapshot_id=latest_snap["id"],
        )
        latest_analysis = await repo.get_latest_analysis_for_policy(policy["id"])
        return PolicyResponse(
            id=policy["id"],
            url=policy["url"],
            canonical_url=policy["canonical_url"],
            title=policy["title"],
            status=policy["status"],
            created_at=policy["created_at"],
            last_checked_at=policy.get("last_checked_at"),
            latest_snapshot_id=policy.get("latest_snapshot_id"),
            latest_analysis=_format_analysis_response(latest_analysis) if latest_analysis else None,
        )

    # Create new snapshot
    new_snapshot = await repo.create_snapshot(
        policy_id=policy["id"],
        content_hash=content_hash,
        extracted_text=normalized_text,
        extractor="http",
        extraction_status="success",
        source_status_code=status_code,
        title=title,
    )

    if is_new_policy or not latest_snap:
        # Initial risk analysis
        ai_res = await analyze_policy_risk(normalized_text)
        analysis_doc = await repo.create_analysis(
            policy_id=policy["id"],
            analysis_type="initial",
            new_snapshot_id=new_snapshot["id"],
            summary=ai_res["summary"],
            findings=ai_res["findings"],
            changes=[],
            model_id=ai_res["model_id"],
            validation_status=ai_res["validation_status"],
        )
        await repo.record_check_event(
            policy_id=policy["id"],
            status="changed",
            message="Initial policy baseline created and analyzed.",
            new_snapshot_id=new_snapshot["id"],
        )
    else:
        # Changed version analysis
        diff_res = compute_policy_diff(latest_snap["extracted_text"], normalized_text)
        ai_res = await explain_policy_changes(
            diff_data=diff_res,
            old_text=latest_snap["extracted_text"],
            new_text=normalized_text,
        )
        analysis_doc = await repo.create_analysis(
            policy_id=policy["id"],
            analysis_type="change",
            old_snapshot_id=latest_snap["id"],
            new_snapshot_id=new_snapshot["id"],
            summary=ai_res["summary"],
            findings=[],
            changes=ai_res["changes"],
            model_id=ai_res["model_id"],
            validation_status=ai_res["validation_status"],
        )
        await repo.record_check_event(
            policy_id=policy["id"],
            status="changed",
            message="New policy version detected and analyzed.",
            old_snapshot_id=latest_snap["id"],
            new_snapshot_id=new_snapshot["id"],
        )

    return PolicyResponse(
        id=policy["id"],
        url=policy["url"],
        canonical_url=policy["canonical_url"],
        title=title,
        status=policy["status"],
        created_at=policy["created_at"],
        last_checked_at=policy.get("last_checked_at"),
        latest_snapshot_id=new_snapshot["id"],
        latest_analysis=_format_analysis_response(analysis_doc),
    )


@router.get("", response_model=List[PolicyResponse])
async def list_policies(limit: int = Query(50, ge=1, le=100)):
    """List tracked policies with latest snapshot and analysis summary."""
    policies = await repo.list_policies(limit=limit)
    res = []
    for p in policies:
        latest_analysis = await repo.get_latest_analysis_for_policy(p["id"])
        res.append(
            PolicyResponse(
                id=p["id"],
                url=p["url"],
                canonical_url=p["canonical_url"],
                title=p["title"],
                status=p["status"],
                created_at=p["created_at"],
                last_checked_at=p.get("last_checked_at"),
                latest_snapshot_id=p.get("latest_snapshot_id"),
                latest_analysis=_format_analysis_response(latest_analysis) if latest_analysis else None,
            )
        )
    return res


@router.get("/{policy_id}", response_model=PolicyResponse)
async def get_policy(policy_id: str):
    """Get policy details and latest analysis."""
    policy = await repo.get_policy_by_id(policy_id)
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")

    latest_analysis = await repo.get_latest_analysis_for_policy(policy_id)
    return PolicyResponse(
        id=policy["id"],
        url=policy["url"],
        canonical_url=policy["canonical_url"],
        title=policy["title"],
        status=policy["status"],
        created_at=policy["created_at"],
        last_checked_at=policy.get("last_checked_at"),
        latest_snapshot_id=policy.get("latest_snapshot_id"),
        latest_analysis=_format_analysis_response(latest_analysis) if latest_analysis else None,
    )


@router.post("/{policy_id}/check", response_model=CheckResponse)
async def check_policy_for_updates(policy_id: str):
    """
    Manually check a tracked policy URL for updates.
    Returns 'unchanged', 'changed', or 'extraction_failed'. Preserves previous baseline upon failure.
    """
    policy = await repo.get_policy_by_id(policy_id)
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")

    latest_snap = await repo.get_snapshot_by_id(policy.get("latest_snapshot_id", "")) if policy.get("latest_snapshot_id") else None
    if not latest_snap:
        raise HTTPException(status_code=400, detail="Policy has no baseline snapshot. Run initial analysis first.")

    # Fetch page
    try:
        html, canonical_url, status_code = await safe_fetch_page(policy["canonical_url"])
        title, extracted_text, warnings = extract_policy_content(html)
    except ExtractionError as exc:
        # Record failure event, preserve old baseline!
        await repo.record_check_event(
            policy_id=policy_id,
            status="extraction_failed",
            message=str(exc),
            old_snapshot_id=latest_snap["id"],
        )
        return CheckResponse(
            status="extraction_failed",
            policy_id=policy_id,
            message=f"Extraction failed: {exc}. Previous version baseline is preserved.",
            old_snapshot_id=latest_snap["id"],
        )
    except Exception as exc:
        logger.error("Recheck unexpected error: %s", exc)
        await repo.record_check_event(
            policy_id=policy_id,
            status="extraction_failed",
            message=str(exc),
            old_snapshot_id=latest_snap["id"],
        )
        return CheckResponse(
            status="extraction_failed",
            policy_id=policy_id,
            message=f"Fetch failed: {exc}",
            old_snapshot_id=latest_snap["id"],
        )

    normalized_text = normalize_policy_text(extracted_text)
    content_hash = compute_content_hash(normalized_text)

    # Hash comparison
    if content_hash == latest_snap["content_hash"]:
        await repo.record_check_event(
            policy_id=policy_id,
            status="unchanged",
            message="No textual changes detected since last snapshot.",
            old_snapshot_id=latest_snap["id"],
            new_snapshot_id=latest_snap["id"],
        )
        return CheckResponse(
            status="unchanged",
            policy_id=policy_id,
            message="No textual changes detected. Content hash is identical to latest snapshot.",
            old_snapshot_id=latest_snap["id"],
            new_snapshot_id=latest_snap["id"],
        )

    # Content changed! Calculate deterministic diff
    diff_res = compute_policy_diff(latest_snap["extracted_text"], normalized_text)

    new_snapshot = await repo.create_snapshot(
        policy_id=policy_id,
        content_hash=content_hash,
        extracted_text=normalized_text,
        extractor="http",
        extraction_status="success",
        source_status_code=status_code,
        title=title,
    )

    ai_res = await explain_policy_changes(
        diff_data=diff_res,
        old_text=latest_snap["extracted_text"],
        new_text=normalized_text,
    )

    analysis_doc = await repo.create_analysis(
        policy_id=policy_id,
        analysis_type="change",
        old_snapshot_id=latest_snap["id"],
        new_snapshot_id=new_snapshot["id"],
        summary=ai_res["summary"],
        findings=[],
        changes=ai_res["changes"],
        model_id=ai_res["model_id"],
        validation_status=ai_res["validation_status"],
    )

    await repo.record_check_event(
        policy_id=policy_id,
        status="changed",
        message="Wording changes detected and analyzed.",
        old_snapshot_id=latest_snap["id"],
        new_snapshot_id=new_snapshot["id"],
    )

    return CheckResponse(
        status="changed",
        policy_id=policy_id,
        message="Textual changes detected and analyzed.",
        old_snapshot_id=latest_snap["id"],
        new_snapshot_id=new_snapshot["id"],
        diff_summary=diff_res["summary"],
        analysis=_format_analysis_response(analysis_doc),
    )


@router.get("/{policy_id}/history", response_model=List[CheckEventResponse])
async def get_policy_history(policy_id: str, limit: int = Query(30, ge=1, le=100)):
    """Get check events and version history for a policy."""
    events = await repo.list_check_events(policy_id, limit=limit)
    return [
        CheckEventResponse(
            id=e["id"],
            policy_id=e["policy_id"],
            checked_at=e["checked_at"],
            status=e["status"],
            message=e.get("message"),
            old_snapshot_id=e.get("old_snapshot_id"),
            new_snapshot_id=e.get("new_snapshot_id"),
        )
        for e in events
    ]


@router.get("/{policy_id}/snapshots/{snapshot_id}", response_model=SnapshotResponse)
async def get_snapshot(policy_id: str, snapshot_id: str):
    """Retrieve full text and metadata for a specific policy snapshot version."""
    snap = await repo.get_snapshot_by_id(snapshot_id)
    if not snap or snap.get("policy_id") != policy_id:
        raise HTTPException(status_code=404, detail="Snapshot not found for this policy")

    return SnapshotResponse(
        id=snap["id"],
        policy_id=snap["policy_id"],
        checked_at=snap["checked_at"],
        content_hash=snap["content_hash"],
        extracted_text=snap.get("extracted_text"),
        extractor=snap.get("extractor", "http"),
        extraction_status=snap.get("extraction_status", "success"),
        source_status_code=snap.get("source_status_code", 200),
        title=snap.get("title"),
    )
