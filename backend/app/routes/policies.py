"""Policy Management, Extraction, Analysis, and Change Tracking Routes."""
from __future__ import annotations
import logging
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, Path
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
from app.services.gemma import analyze_policy_risk, explain_policy_changes, is_ai_configured
from app.db.repositories import repo

logger = logging.getLogger("easyfineprint.policies")
router = APIRouter(prefix="/policies", tags=["policies"])

POLICY_ID_PATTERN = r"^pol_[a-zA-Z0-9_-]{4,32}$"
SNAPSHOT_ID_PATTERN = r"^snp_[a-zA-Z0-9_-]{4,32}$"


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
        risk_score=analysis_doc.get("risk_score"),
        risk_level=analysis_doc.get("risk_level"),
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

    # 1. Look up policy by canonical_url or raw_url
    policy = await repo.get_policy_by_url(canonical_url)
    if not policy and raw_url != canonical_url:
        policy = await repo.get_policy_by_url(raw_url)

    # 2. Find latest snapshot for this policy if tracked
    latest_snap = None
    if policy:
        latest_snap = await repo.get_latest_snapshot_for_policy(policy["id"])

    # 3. Check for exact character-for-character match in DB
    is_exact_match = False
    if latest_snap and latest_snap.get("extracted_text"):
        if latest_snap["extracted_text"] == normalized_text or latest_snap.get("content_hash") == content_hash:
            is_exact_match = True

    # If policy wasn't resolved by URL, check if ANY snapshot in DB matches exact text & hash
    if not is_exact_match and not policy:
        existing_snap = await repo.get_snapshot_by_hash(content_hash)
        if existing_snap and (existing_snap.get("extracted_text") == normalized_text or existing_snap.get("content_hash") == content_hash):
            matched_policy = await repo.get_policy_by_id(existing_snap["policy_id"])
            if matched_policy:
                policy = matched_policy
                latest_snap = existing_snap
                is_exact_match = True

    # 4. IF EXACT MATCH: REUSE BASELINE IMMEDIATELY (0 AI calls, instant response, consistent score)
    if is_exact_match and policy and latest_snap:
        latest_analysis = await repo.get_latest_analysis_for_policy(policy["id"])
        # If an analysis exists, reuse it immediately:
        # (Only re-analyze if AI credentials are newly configured and existing was deterministic-fallback)
        should_upgrade = (
            is_ai_configured()
            and latest_analysis is not None
            and latest_analysis.get("model_id") == "deterministic-fallback"
        )
        if latest_analysis and not should_upgrade:
            logger.info(
                "Exact character-for-character match for %s. Reusing baseline analysis instantly.",
                policy.get("canonical_url"),
            )
            await repo.record_check_event(
                policy_id=policy["id"],
                status="unchanged",
                message="No textual changes detected compared to existing baseline.",
                old_snapshot_id=latest_snap["id"],
                new_snapshot_id=latest_snap["id"],
            )
            await repo.update_policy(policy["id"], {
                "last_checked_at": datetime.now(timezone.utc),
                "latest_snapshot_id": latest_snap["id"],
                "title": title or policy.get("title"),
            })
            return PolicyResponse(
                id=policy["id"],
                url=policy["url"],
                canonical_url=policy["canonical_url"],
                title=policy["title"],
                status=policy["status"],
                created_at=policy["created_at"],
                last_checked_at=datetime.now(timezone.utc),
                latest_snapshot_id=latest_snap["id"],
                latest_analysis=_format_analysis_response(latest_analysis),
                reanalysis_status="skipped_unchanged",
            )

    # 5. NEW POLICY OR GENUINE TEXT CHANGE:
    if not policy:
        policy = await repo.create_policy(url=raw_url, canonical_url=canonical_url, title=title)
        is_new_policy = True
    else:
        is_new_policy = False

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
            risk_score=ai_res.get("risk_score"),
            risk_level=ai_res.get("risk_level"),
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
            message="Textual changes detected and analyzed.",
            old_snapshot_id=latest_snap["id"],
            new_snapshot_id=new_snapshot["id"],
        )

    await repo.update_policy(policy["id"], {
        "latest_snapshot_id": new_snapshot["id"],
        "last_checked_at": datetime.now(timezone.utc),
        "title": title,
    })

    return PolicyResponse(
        id=policy["id"],
        url=policy["url"],
        canonical_url=policy["canonical_url"],
        title=title,
        status=policy["status"],
        created_at=policy["created_at"],
        last_checked_at=datetime.now(timezone.utc),
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
async def get_policy(
    policy_id: str = Path(..., pattern=POLICY_ID_PATTERN, description="Unique policy identifier"),
):
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
async def check_policy_for_updates(
    policy_id: str = Path(..., pattern=POLICY_ID_PATTERN, description="Unique policy identifier"),
):
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

    # Hash and character-for-character comparison
    if content_hash == latest_snap["content_hash"] or normalized_text == latest_snap.get("extracted_text"):
        await repo.record_check_event(
            policy_id=policy_id,
            status="unchanged",
            message="No textual changes detected since last snapshot.",
            old_snapshot_id=latest_snap["id"],
            new_snapshot_id=latest_snap["id"],
        )
        await repo.update_policy(policy_id, {
            "last_checked_at": datetime.now(timezone.utc),
        })
        return CheckResponse(
            status="unchanged",
            policy_id=policy_id,
            message="No textual changes detected. Content is identical to latest snapshot.",
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

    await repo.update_policy(policy_id, {
        "latest_snapshot_id": new_snapshot["id"],
        "last_checked_at": datetime.now(timezone.utc),
        "title": title or policy.get("title"),
    })

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
async def get_policy_history(
    policy_id: str = Path(..., pattern=POLICY_ID_PATTERN, description="Unique policy identifier"),
    limit: int = Query(30, ge=1, le=100),
):
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
async def get_snapshot(
    policy_id: str = Path(..., pattern=POLICY_ID_PATTERN, description="Unique policy identifier"),
    snapshot_id: str = Path(..., pattern=SNAPSHOT_ID_PATTERN, description="Unique snapshot identifier"),
):
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


@router.post("/{policy_id}/reanalyze", response_model=PolicyResponse)
async def reanalyze_policy(
    policy_id: str = Path(..., pattern=POLICY_ID_PATTERN, description="Unique policy identifier"),
):
    """
    Re-run deep semantic single-pass clause analysis and risk scoring on an existing policy snapshot.
    If the snapshot was already analyzed and no text changed, skips redundant AI execution and preserves the existing score.
    """
    policy = await repo.get_policy_by_id(policy_id)
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")

    snap_id = policy.get("latest_snapshot_id")
    if not snap_id:
        raise HTTPException(status_code=400, detail="Policy has no baseline snapshot.")

    snapshot = await repo.get_snapshot_by_id(snap_id)
    if not snapshot or not snapshot.get("extracted_text"):
        raise HTTPException(status_code=400, detail="Snapshot text unavailable.")

    # 1. Actually fetch the live page from the web and verify character-for-character against DB
    is_live_identical = True
    active_text = snapshot["extracted_text"]
    try:
        html, canonical_url, status_code = await safe_fetch_page(policy["canonical_url"])
        title, extracted_text, warnings = extract_policy_content(html)
        live_norm = normalize_policy_text(extracted_text)
        live_hash = compute_content_hash(live_norm)
        is_live_identical = (
            live_hash == snapshot.get("content_hash")
            or live_norm == snapshot.get("extracted_text")
        )
        if not is_live_identical:
            active_text = live_norm
    except Exception as exc:
        logger.info("Could not re-fetch live page during re-analysis (%s); verifying against DB snapshot.", exc)
        is_live_identical = True

    # 2. Check if a valid previous analysis exists for this snapshot
    latest_analysis = await repo.get_latest_analysis_for_policy(policy_id)
    should_upgrade = (
        is_ai_configured()
        and latest_analysis is not None
        and latest_analysis.get("model_id") == "deterministic-fallback"
    )
    has_valid_previous_analysis = (
        latest_analysis is not None
        and latest_analysis.get("new_snapshot_id") == snap_id
        and not should_upgrade
    )

    # 3. Industry standard: If live fetched text matches DB snapshot character-for-character,
    # and a valid analysis already exists, do not re-analyze and preserve existing score.
    if is_live_identical and has_valid_previous_analysis:
        logger.info(
            "Re-analysis verified live page for %s: text is identical character-for-character to DB snapshot. Preserving existing baseline analysis.",
            policy.get("canonical_url"),
        )
        return PolicyResponse(
            id=policy["id"],
            url=policy["url"],
            canonical_url=policy["canonical_url"],
            title=policy["title"],
            status=policy["status"],
            created_at=policy["created_at"],
            last_checked_at=policy.get("last_checked_at"),
            latest_snapshot_id=snap_id,
            latest_analysis=_format_analysis_response(latest_analysis),
            reanalysis_status="skipped_unchanged",
        )

    # 4. Otherwise (fallback upgrade, text changed, or explicit force), run single-pass analysis on verified text:
    ai_res = await analyze_policy_risk(active_text)
    analysis_doc = await repo.create_analysis(
        policy_id=policy_id,
        analysis_type="initial",
        new_snapshot_id=snap_id,
        summary=ai_res["summary"],
        risk_score=ai_res.get("risk_score"),
        risk_level=ai_res.get("risk_level"),
        findings=ai_res["findings"],
        changes=[],
        model_id=ai_res["model_id"],
        validation_status=ai_res["validation_status"],
    )

    await repo.record_check_event(
        policy_id=policy_id,
        status="reanalyzed",
        message="Refreshed AI clause analysis and risk scoring (single-pass Gemma 4 evaluation).",
        new_snapshot_id=snap_id,
    )

    await repo.update_policy(policy_id, {
        "last_checked_at": datetime.now(timezone.utc),
    })

    return PolicyResponse(
        id=policy["id"],
        url=policy["url"],
        canonical_url=policy["canonical_url"],
        title=policy["title"],
        status=policy["status"],
        created_at=policy["created_at"],
        last_checked_at=datetime.now(timezone.utc),
        latest_snapshot_id=snap_id,
        latest_analysis=_format_analysis_response(analysis_doc),
        reanalysis_status="reanalyzed",
    )
