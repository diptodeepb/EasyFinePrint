"""Policy discovery search route for company name lookup."""
from __future__ import annotations
from fastapi import APIRouter
from app.schemas.policy import DiscoverySearchRequest, DiscoveryResponse, DiscoveryCandidate
from app.services.discovery import discover_policy_urls

router = APIRouter(prefix="/discovery", tags=["discovery"])


@router.post("/search", response_model=DiscoveryResponse)
async def search_policy_urls(req: DiscoverySearchRequest):
    """
    Search for candidate legal policy URLs by company or product name.
    Utilizes an authoritative directory and live heuristic crawler.
    """
    result = await discover_policy_urls(req.query)

    candidates = [
        DiscoveryCandidate(
            title=c["title"],
            url=c["url"],
            snippet=c.get("snippet"),
            source=c.get("source", "discovery"),
        )
        for c in result.get("candidates", [])
    ]

    return DiscoveryResponse(
        query=req.query,
        candidates=candidates,
        cached=result.get("cached", False),
    )
