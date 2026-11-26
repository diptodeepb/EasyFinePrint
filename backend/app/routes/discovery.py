"""Policy discovery search route for company name lookup."""
from __future__ import annotations
from fastapi import APIRouter
from app.schemas.policy import DiscoverySearchRequest, DiscoveryResponse, DiscoveryCandidate
from app.services.discovery import discover_policy_urls
from app.security.sanitizers import strip_control_chars

router = APIRouter(prefix="/discovery", tags=["discovery"])


@router.post("/search", response_model=DiscoveryResponse)
async def search_policy_urls(req: DiscoverySearchRequest):
    """
    Search for candidate legal policy URLs by company or product name.
    Utilizes an authoritative directory and live heuristic direct website inspection.
    """
    result = await discover_policy_urls(req.query)

    candidates = [
        DiscoveryCandidate(
            title=strip_control_chars(c["title"], allow_newlines=False, max_length=200),
            url=c["url"],
            snippet=strip_control_chars(c.get("snippet"), allow_newlines=False, max_length=400) if c.get("snippet") else None,
            source=c.get("source", "discovery"),
        )
        for c in result.get("candidates", [])
    ]

    return DiscoveryResponse(
        query=req.query,
        candidates=candidates,
        total=result.get("total", len(candidates)),
        cached=result.get("cached", False),
    )
