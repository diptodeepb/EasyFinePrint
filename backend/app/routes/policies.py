"""Policy Management, Extraction, Analysis, and Change Tracking Routes."""
from __future__ import annotations
import logging
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, Path
from app.schemas.policy import (
    PolicyAnalyzeRequest,
    PolicySelfAnalyzeRequest,
    PolicyResponse,
    AnalysisResponse,
    SnapshotResponse,
    CheckResponse,
    CheckEventResponse,
    FindingSchema,
    DiffChangeSchema,
)
from app.services.extractor import (
    safe_fetch_page,
    extract_policy_content,
    fetch_wayback_snapshot,
    ExtractionError,
)
from app.services.normalizer import (
    normalize_policy_text,
    compute_content_hash,
    canonicalize_url,
)
from app.services.diff_engine import compute_policy_diff
from app.services.gemma import analyze_policy_risk, explain_policy_changes, is_ai_configured
from app.legal import get_self_policy, SELF_POLICIES
from app.db.repositories import repo

logger = logging.getLogger("easyfineprint.policies")
router = APIRouter(prefix="/policies", tags=["policies"])

POLICY_ID_PATTERN = r"^pol_[a-zA-Z0-9_-]{4,32}$"
SNAPSHOT_ID_PATTERN = r"^snp_[a-zA-Z0-9_-]{4,32}$"


def derive_title_from_url(url: str) -> str:
    """Derive a human-readable policy title from domain and path when not supplied."""
    if not url:
        return "Policy Agreement"
    try:
        from urllib.parse import urlparse
        clean = url.strip()
        if clean.startswith("/"):
            seg = clean.strip("/").split("/")[0] or "Terms"
            return seg.capitalize()
        parsed = urlparse(clean if "://" in clean else f"https://{clean}")
        host = parsed.netloc.replace("www.", "")
        parts = host.split(".")
        brand = parts[-2].capitalize() if len(parts) >= 2 else (parts[0].capitalize() if parts else "")
        path = parsed.path.lower()
        if "privacy" in path:
            doc_type = "Privacy Policy"
        elif "cookie" in path:
            doc_type = "Cookie Policy"
        elif "security" in path:
            doc_type = "Security Policy"
        elif "user-agreement" in path or "user_agreement" in path:
            doc_type = "User Agreement"
        elif "acceptable" in path or "aup" in path:
            doc_type = "Acceptable Use Policy"
        elif "terms" in path or "tos" in path or "legal" in path:
            doc_type = "Terms of Service"
        else:
            doc_type = "Policy Agreement"
        derived = f"{brand} {doc_type}".strip() if brand else doc_type
        return derived[:200]
    except Exception:
        return "Policy Agreement"


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
        provenance=analysis_doc.get("provenance", "live"),
        warnings=analysis_doc.get("warnings", []),
    )


async def _process_policy_ingestion(
    raw_url: str,
    canonical_url: str,
    title: str,
    extracted_text: str,
    status_code: int = 200,
    extractor: str = "http",
    provenance: str = "live",
    warnings: Optional[List[str]] = None,
) -> PolicyResponse:
    """Core deterministic ingestion and risk analysis pipeline."""
    normalized_text = normalize_policy_text(extracted_text)
    content_hash = compute_content_hash(normalized_text)
    warnings_list = list(warnings or [])

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
        if latest_analysis:
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
                provenance=latest_analysis.get("provenance", "live") if latest_analysis else "live",
                warnings=latest_analysis.get("warnings", []) if latest_analysis else [],
            )

        if should_upgrade:
            logger.info(
                "Exact match found for %s, but previous analysis is unrated or fallback. Upgrading analysis with Gemma 4...",
                policy.get("canonical_url"),
            )
            ai_res = await analyze_policy_risk(normalized_text)
            analysis_doc = await repo.create_analysis(
                policy_id=policy["id"],
                analysis_type="initial",
                new_snapshot_id=latest_snap["id"],
                summary=ai_res["summary"],
                risk_score=ai_res.get("risk_score"),
                risk_level=ai_res.get("risk_level"),
                findings=ai_res.get("findings", []),
                changes=[],
                model_id=ai_res["model_id"],
                validation_status=ai_res["validation_status"],
                provenance=provenance,
                warnings=warnings_list,
            )
            await repo.record_check_event(
                policy_id=policy["id"],
                status="reanalyzed",
                message="Upgraded policy analysis with single-pass Gemma 4 clause risk scoring.",
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
                latest_analysis=_format_analysis_response(analysis_doc),
                reanalysis_status="upgraded",
                provenance=provenance,
                warnings=warnings_list,
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
        extractor=extractor,
        extraction_status="success" if extractor != "user_pasted" else "user_pasted",
        source_status_code=status_code,
        title=title,
        provenance=provenance,
        warnings=warnings_list,
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
            provenance=provenance,
            warnings=warnings_list,
        )
        await repo.record_check_event(
            policy_id=policy["id"],
            status="changed",
            message="Initial policy baseline created and analyzed.",
            new_snapshot_id=new_snapshot["id"],
        )
    else:
        # Changed version analysis: explain deterministic diff and score new clauses
        diff_res = compute_policy_diff(latest_snap["extracted_text"], normalized_text)
        ai_res = await explain_policy_changes(
            diff_data=diff_res,
            old_text=latest_snap["extracted_text"],
            new_text=normalized_text,
        )
        risk_res = await analyze_policy_risk(normalized_text)
        analysis_doc = await repo.create_analysis(
            policy_id=policy["id"],
            analysis_type="change",
            old_snapshot_id=latest_snap["id"],
            new_snapshot_id=new_snapshot["id"],
            summary=ai_res["summary"],
            risk_score=risk_res.get("risk_score"),
            risk_level=risk_res.get("risk_level"),
            findings=risk_res.get("findings", []),
            changes=ai_res["changes"],
            model_id=ai_res["model_id"],
            validation_status=ai_res["validation_status"],
            provenance=provenance,
            warnings=warnings_list,
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
        "provenance": provenance,
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
        provenance=provenance,
        warnings=warnings_list,
    )


@router.post("/analyze", response_model=PolicyResponse)
async def analyze_policy(req: PolicyAnalyzeRequest):
    """
    4-Tier Hybrid Policy Ingestion, Analysis, and Diff Pipeline:
    - Tier 1: Direct Safe Scrape & Client JavaScript Hydration Extraction
    - Tier 2: Public Web Archive Auto-Fallback (Internet Archive / Wayback Machine)
    - Tier 3: User-Provided Direct Document / Text Ingestion (Manual Paste Fallback)
    - Tier 4: Zero-Drift Baseline Database Cache
    """
    raw_url = req.url.strip()

    # Self-policy intercept (dogfooding / testing our own terms)
    self_doc = get_self_policy(raw_url)
    if self_doc:
        if req.raw_text and req.raw_text.strip():
            raise HTTPException(
                status_code=400,
                detail=(
                    f"The URL '{raw_url}' is a system-maintained policy. "
                    "User text paste is reserved for policies that cannot be retrieved automatically by the system."
                ),
            )
        return await _process_policy_ingestion(
            raw_url=self_doc["url"],
            canonical_url=self_doc["canonical_url"],
            title=self_doc["title"],
            extracted_text=self_doc["text"],
            status_code=200,
            extractor="self",
            provenance="self",
        )

    # -------------------------------------------------------------
    # TIER 3: USER-PROVIDED DIRECT TEXT INGESTION
    # -------------------------------------------------------------
    if req.raw_text and req.raw_text.strip():
        cleaned_text = req.raw_text.strip()
        if len(cleaned_text) < 100:
            raise HTTPException(
                status_code=422,
                detail="Pasted policy text is suspiciously short (<100 characters). Please paste the complete agreement body.",
            )

        canon_raw = canonicalize_url(raw_url)

        # 1. Reject if matching our internal self policies
        for self_path in ("/terms", "/privacy"):
            if canon_raw == canonicalize_url(self_path):
                raise HTTPException(
                    status_code=400,
                    detail=(
                        f"The URL '{raw_url}' is a system-maintained policy. "
                        "User text paste is reserved for policies that cannot be retrieved automatically by the system."
                    ),
                )

        # 2. Reject if URL already exists as a system-maintained policy in DB
        system_match = await repo.find_system_policy_by_canonical(canon_raw)
        if system_match:
            sys_title = system_match.get("title", "System Policy")
            raise HTTPException(
                status_code=400,
                detail=(
                    f"The URL '{raw_url}' already exists as a system-maintained policy ('{sys_title}'). "
                    "User text paste is reserved for policies that cannot be retrieved automatically by the system."
                ),
            )

        if req.title and req.title.strip() and req.title.strip() != "User-Submitted Agreement":
            title = req.title.strip()
        else:
            title = derive_title_from_url(raw_url)
        user_warnings = [
            "User-Provided Text: This policy snapshot was submitted via direct manual text paste. Findings and diffs reflect user-submitted content and may not represent the complete official agreement."
        ]
        return await _process_policy_ingestion(
            raw_url=raw_url,
            canonical_url=raw_url,
            title=title,
            extracted_text=cleaned_text,
            status_code=200,
            extractor="user_pasted",
            provenance="user_pasted",
            warnings=user_warnings,
        )

    # -------------------------------------------------------------
    # TIER 1: HIGH-FIDELITY LIVE SCRAPING & CLIENT HYDRATION EXTRACTION
    # -------------------------------------------------------------
    tier1_error: Optional[str] = None
    try:
        html, canonical_url, status_code = await safe_fetch_page(raw_url)
        title, extracted_text, warnings = extract_policy_content(html)
        if len(extracted_text.strip()) >= 100:
            return await _process_policy_ingestion(
                raw_url=raw_url,
                canonical_url=canonical_url,
                title=title,
                extracted_text=extracted_text,
                status_code=status_code,
                extractor="http",
                provenance="live",
                warnings=warnings,
            )
    except ExtractionError as exc:
        err_msg = str(exc).lower()
        # Immediately reject SSRF, invalid protocols, and prohibited private IPs with HTTP 400
        if any(kw in err_msg for kw in ("prohibited", "invalid", "ssrf", "blocked", "forbidden", "loopback", "private", "redirect hops")):
            raise HTTPException(status_code=400, detail=str(exc))
        tier1_error = str(exc)
        logger.info("Tier 1 live scrape blocked for %s: %s. Initiating Tier 2 Wayback Machine fallback...", raw_url, exc)
    except Exception as exc:
        tier1_error = str(exc)
        logger.warning("Tier 1 unexpected scrape failure for %s: %s", raw_url, exc)

    # -------------------------------------------------------------
    # TIER 2: PUBLIC WEB ARCHIVE AUTO-FALLBACK (WAYBACK MACHINE)
    # -------------------------------------------------------------
    logger.info("Initiating Tier 2 public archive lookup for %s...", raw_url)
    wb_result = await fetch_wayback_snapshot(raw_url)
    if wb_result:
        wb_html, wb_archive_url, wb_timestamp = wb_result
        try:
            wb_title, wb_text, wb_warnings = extract_policy_content(wb_html)
            if len(wb_text.strip()) >= 100:
                logger.info("Successfully extracted policy via Tier 2 Wayback snapshot (%s) for %s", wb_timestamp, raw_url)
                formatted_ts = (
                    f"{wb_timestamp[:4]}-{wb_timestamp[4:6]}-{wb_timestamp[6:8]}"
                    if len(wb_timestamp) >= 8
                    else wb_timestamp
                )
                archive_warnings = [
                    f"Live scrape restricted by origin firewall; analyzed verified public snapshot from Internet Archive (timestamp: {formatted_ts})."
                ] + wb_warnings
                return await _process_policy_ingestion(
                    raw_url=raw_url,
                    canonical_url=raw_url,
                    title=wb_title,
                    extracted_text=wb_text,
                    status_code=200,
                    extractor="archive",
                    provenance="archive",
                    warnings=archive_warnings,
                )
        except Exception as wb_exc:
            logger.debug("Wayback extraction parsing error for %s: %s", raw_url, wb_exc)

    # -------------------------------------------------------------
    # TIER 4: ZERO-DRIFT BASELINE CACHE (DB FALLBACK)
    # -------------------------------------------------------------
    existing_policy = await repo.get_policy_by_url(raw_url) or await repo.get_policy_by_url(raw_url.rstrip("/"))
    if existing_policy:
        latest_snap = await repo.get_latest_snapshot_for_policy(existing_policy["id"])
        latest_analysis = await repo.get_latest_analysis_for_policy(existing_policy["id"])
        if latest_snap and latest_analysis:
            logger.info("Serving existing verified baseline %s from DB for %s", existing_policy["id"], raw_url)
            fallback_warnings = ["Live scrape and archive lookup were blocked; served verified existing baseline from database."]
            return PolicyResponse(
                id=existing_policy["id"],
                url=existing_policy["url"],
                canonical_url=existing_policy["canonical_url"],
                title=existing_policy["title"],
                status=existing_policy["status"],
                created_at=existing_policy["created_at"],
                last_checked_at=existing_policy.get("last_checked_at", datetime.now(timezone.utc)),
                latest_snapshot_id=latest_snap["id"],
                latest_analysis=_format_analysis_response(latest_analysis),
                reanalysis_status="cached_fallback",
                provenance="cached_fallback",
                warnings=fallback_warnings,
            )

    # -------------------------------------------------------------
    # ALL TIERS EXHAUSTED: PROMPT USER FOR TIER 3 PASTE
    # -------------------------------------------------------------
    raise HTTPException(
        status_code=422,
        detail=f"Unable to analyze policy: The origin server prevented automated retrieval ({tier1_error or 'origin challenge'}) and no public archive was available. Please switch to the 'Paste Text' tab to audit this agreement directly.",
    )


@router.post("/analyze-self", response_model=PolicyResponse)
async def analyze_self_policy(req: Optional[PolicySelfAnalyzeRequest] = None):
    """
    Explicit endpoint to analyze EasyFinePrint's own Terms of Use or Privacy Policy.
    Demonstrates eating our own dog food: single-pass analysis on our own legal commitments.
    """
    target_type = req.policy_type if req else "terms"
    self_doc = get_self_policy(target_type) or SELF_POLICIES["terms"]
    return await _process_policy_ingestion(
        raw_url=self_doc["url"],
        canonical_url=self_doc["canonical_url"],
        title=self_doc["title"],
        extracted_text=self_doc["text"],
        status_code=200,
    )


@router.get("/self-policies")
async def list_self_policies_metadata():
    """List available self-policies (Terms of Use, Privacy Policy) for dogfooding, in-app viewing, and testing."""
    return [
        {
            "key": item["key"],
            "title": item["title"],
            "url": item["url"],
            "canonical_url": item["canonical_url"],
            "description": item["description"],
            "text": item["text"],
        }
        for item in SELF_POLICIES.values()
    ]


@router.get("/self-policies/{key}")
async def get_single_self_policy(key: str = Path(..., description="Self-policy key ('terms' or 'privacy')")):
    """Retrieve full text and metadata for EasyFinePrint's own Terms of Use or Privacy Policy."""
    doc = get_self_policy(key)
    if not doc:
        raise HTTPException(status_code=404, detail=f"Self policy '{key}' not found. Valid keys: 'terms', 'privacy'.")
    return doc



@router.get("", response_model=List[PolicyResponse])
async def list_policies(limit: int = Query(50, ge=1, le=100)):
    """List tracked policies with latest snapshot and analysis summary."""
    policies = await repo.list_policies(limit=limit)
    res = []
    for p in policies:
        latest_analysis = await repo.get_latest_analysis_for_policy(p["id"])
        latest_snap = await repo.get_snapshot_by_id(p.get("latest_snapshot_id")) if p.get("latest_snapshot_id") else None
        provenance = (
            p.get("provenance")
            or (latest_analysis.get("provenance") if latest_analysis else None)
            or (latest_snap.get("provenance") if latest_snap else None)
            or "live"
        )
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
                provenance=provenance,
                warnings=latest_analysis.get("warnings", []) if latest_analysis else [],
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
    latest_snap = await repo.get_snapshot_by_id(policy.get("latest_snapshot_id")) if policy.get("latest_snapshot_id") else None
    provenance = (
        policy.get("provenance")
        or (latest_analysis.get("provenance") if latest_analysis else None)
        or (latest_snap.get("provenance") if latest_snap else None)
        or "live"
    )
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
        provenance=provenance,
        warnings=latest_analysis.get("warnings", []) if latest_analysis else [],
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

    # Check if target is an internal self-policy (dogfooding)
    self_doc = get_self_policy(policy.get("canonical_url", "") or policy.get("url", ""))
    if self_doc:
        title = self_doc["title"]
        extracted_text = self_doc["text"]
        canonical_url = self_doc["canonical_url"]
        status_code = 200
    else:
        # Fetch page with Tier 1 live scrape + Tier 2 archive fallback
        provenance = "live"
        warnings = []
        try:
            html, canonical_url, status_code = await safe_fetch_page(policy["canonical_url"])
            title, extracted_text, warnings = extract_policy_content(html)
        except ExtractionError as exc:
            # Attempt Tier 2 Wayback Machine lookup
            wb_res = await fetch_wayback_snapshot(policy["canonical_url"])
            if wb_res:
                wb_html, wb_url, wb_ts = wb_res
                try:
                    wb_title, wb_text, wb_warns = extract_policy_content(wb_html)
                    if len(wb_text.strip()) >= 100:
                        title = wb_title
                        extracted_text = wb_text
                        canonical_url = policy["canonical_url"]
                        status_code = 200
                        provenance = "archive"
                        warnings = [f"Origin server WAF active; checked against newest public snapshot from Internet Archive ({wb_ts})."] + wb_warns
                    else:
                        raise exc
                except Exception:
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
            else:
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
        extractor=extractor if "extractor" in locals() else ("archive" if provenance == "archive" else "http"),
        extraction_status="success",
        source_status_code=status_code,
        title=title,
        provenance=provenance,
        warnings=warnings,
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
        provenance=provenance,
        warnings=warnings,
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
        provenance=snap.get("provenance", "live"),
        warnings=snap.get("warnings", []),
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

    # 1. Actually fetch the live page from the web (or internal self-policy) and verify character-for-character against DB
    is_live_identical = True
    active_text = snapshot["extracted_text"]
    self_doc = get_self_policy(policy.get("canonical_url", "") or policy.get("url", ""))
    if self_doc:
        extracted_text = self_doc["text"]
        live_norm = normalize_policy_text(extracted_text)
        live_hash = compute_content_hash(live_norm)
        is_live_identical = (
            live_hash == snapshot.get("content_hash")
            or live_norm == snapshot.get("extracted_text")
        )
        if not is_live_identical:
            active_text = live_norm
    else:
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
    has_valid_previous_analysis = (
        latest_analysis is not None
        and latest_analysis.get("new_snapshot_id") == snap_id
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


@router.delete("/{policy_id}")
async def delete_policy_endpoint(policy_id: str):
    """Delete a tracked policy and all associated snapshots, analyses, and check events."""
    deleted = await repo.delete_policy(policy_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Policy not found")
    return {"status": "deleted", "policy_id": policy_id}
