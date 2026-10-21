"""Policy discovery search route using optional SerpApi fallback."""
from __future__ import annotations
from fastapi import APIRouter, HTTPException
from app.schemas.policy import DiscoverySearchRequest, DiscoveryResponse, DiscoveryCandidate
from app.services.serpapi import discover_policy_urls

router = APIRouter(prefix="/discovery", tags=["discovery"])


@router.post("/search", response_model=DiscoveryResponse)
async def search_policy_urls(req: DiscoverySearchRequest):
    """
    Search for candidate policy URLs by company or product name.
    Strictly opt-in, quota-limited, and cached.
    """
    result = await discover_policy_urls(req.query)

    if "error" in result:
        # Graceful return with warning message rather than 500
        return DiscoveryResponse(
            query=req.query,
            candidates=[],
            cached=False,
            quota_remaining=0,
        )

    candidates = [
        DiscoveryCandidate(
            title=c["title"],
            url=c["url"],
            snippet=c.get("snippet"),
            source=c.get("source", "serpapi"),
        )
        for c in result.get("candidates", [])
    ]

    return DiscoveryResponse(
        query=req.query,
        candidates=candidates,
        cached=result.get("cached", False),
        quota_remaining=result.get("quota_remaining"),
    )
