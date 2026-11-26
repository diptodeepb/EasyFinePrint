"""Pytest configuration and global fixtures for EasyFinePrint backend tests."""
import pytest
from unittest.mock import patch
from app.db.repositories import repo
from app.security.rate_limiter import rate_limiter


@pytest.fixture(autouse=True)
def isolated_test_db():
    """Ensure automated tests run against isolated in-memory stores and never pollute MongoDB."""
    repo._mem_policies.clear()
    repo._mem_snapshots.clear()
    repo._mem_analyses.clear()
    repo._mem_check_events.clear()
    repo._mem_usage.clear()
    rate_limiter.clear()

    with patch.object(repo, "_use_mongo", return_value=False):
        yield

    repo._mem_policies.clear()
    repo._mem_snapshots.clear()
    repo._mem_analyses.clear()
    repo._mem_check_events.clear()
    repo._mem_usage.clear()
    rate_limiter.clear()
