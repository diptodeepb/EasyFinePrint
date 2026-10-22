"""Pydantic schemas for request/response validation."""
from __future__ import annotations
from datetime import datetime
from typing import List, Literal, Optional
from pydantic import BaseModel, Field, HttpUrl


FindingCategory = Literal[
    "renewal",
    "cancellation",
    "data",
    "price_change",
    "disputes",
    "liability",
    "termination",
    "safety",
    "other",
]

SeverityLevel = Literal["low", "medium", "high", "uncertain"]
ValidationStatus = Literal["passed", "partial", "failed", "skipped"]
CheckStatus = Literal["unchanged", "changed", "reanalyzed", "extraction_failed", "analysis_failed"]


class FindingSchema(BaseModel):
    category: FindingCategory
    severity: SeverityLevel
    exact_excerpt: str = Field(..., min_length=10, description="Verbatim quote from the policy text")
    explanation: str
    why_it_might_matter: str
    uncertainty: Optional[str] = None


class DiffChangeSchema(BaseModel):
    change_id: str
    change_type: Literal["addition", "removal", "modification"]
    old_text: Optional[str] = None
    new_text: Optional[str] = None
    explanation: Optional[str] = None
    possible_implication: Optional[str] = None
    exact_excerpt: Optional[str] = None
    source_version: Optional[Literal["old", "new"]] = None
    uncertainty: Optional[str] = None
    significance: Optional[SeverityLevel] = "uncertain"


class PolicyAnalyzeRequest(BaseModel):
    url: str = Field(..., description="Target public policy URL")


class AnalysisResponse(BaseModel):
    id: str
    policy_id: str
    analysis_type: Literal["initial", "change"]
    old_snapshot_id: Optional[str] = None
    new_snapshot_id: str
    summary: str
    risk_score: Optional[int] = Field(None, ge=0, le=100)
    risk_level: Optional[Literal["low", "moderate", "elevated", "high"]] = None
    findings: List[FindingSchema] = []
    changes: List[DiffChangeSchema] = []
    model_id: str
    created_at: datetime
    validation_status: ValidationStatus


class PolicyResponse(BaseModel):
    id: str
    url: str
    canonical_url: str
    title: str
    status: str
    created_at: datetime
    last_checked_at: Optional[datetime] = None
    latest_snapshot_id: Optional[str] = None
    latest_analysis: Optional[AnalysisResponse] = None
    reanalysis_status: Optional[str] = None


class SnapshotResponse(BaseModel):
    id: str
    policy_id: str
    checked_at: datetime
    content_hash: str
    extracted_text: Optional[str] = None
    extractor: str
    extraction_status: str
    source_status_code: int
    title: Optional[str] = None


class CheckEventResponse(BaseModel):
    id: str
    policy_id: str
    checked_at: datetime
    status: CheckStatus
    message: Optional[str] = None
    old_snapshot_id: Optional[str] = None
    new_snapshot_id: Optional[str] = None


class CheckResponse(BaseModel):
    status: CheckStatus
    policy_id: str
    message: str
    old_snapshot_id: Optional[str] = None
    new_snapshot_id: Optional[str] = None
    diff_summary: Optional[dict] = None
    analysis: Optional[AnalysisResponse] = None


class DiscoverySearchRequest(BaseModel):
    query: str = Field(..., min_length=2, max_length=120, description="Company or service name")


class DiscoveryCandidate(BaseModel):
    title: str
    url: str
    snippet: Optional[str] = None
    source: str = "discovery"


class DiscoveryResponse(BaseModel):
    query: str
    candidates: List[DiscoveryCandidate]
    cached: bool = False
