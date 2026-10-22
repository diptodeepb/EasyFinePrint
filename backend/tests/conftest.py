"""Pytest configuration and global fixtures for EasyFinePrint backend tests."""
import pytest
from unittest.mock import patch
from app.db.repositories import repo


@pytest.fixture(autouse=True)
def isolated_test_db():
    """Ensure automated tests run against isolated in-memory stores and never pollute MongoDB."""
    # Reset in-memory stores before each test
    repo._mem_policies.clear()
    repo._mem_snapshots.clear()
    repo._mem_analyses.clear()
    repo._mem_check_events.clear()
    repo._mem_usage.clear()

    with patch.object(repo, "_use_mongo", return_value=False):
        yield

    # Clean up after test
    repo._mem_policies.clear()
    repo._mem_snapshots.clear()
    repo._mem_analyses.clear()
    repo._mem_check_events.clear()
    repo._mem_usage.clear()
