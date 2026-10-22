"""MongoDB connection management using Motor (asyncio driver)."""
from __future__ import annotations
import logging
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo import ASCENDING, IndexModel
from app.config import settings

logger = logging.getLogger("easyfineprint.db")

import asyncio

_client: Optional[AsyncIOMotorClient] = None
_client_loop: Optional[asyncio.AbstractEventLoop] = None


def get_client() -> AsyncIOMotorClient:
    global _client, _client_loop
    try:
        current_loop = asyncio.get_running_loop()
    except RuntimeError:
        current_loop = None

    if _client is None or (_client_loop is not None and current_loop is not None and _client_loop != current_loop):
        if _client is not None:
            try:
                _client.close()
            except Exception:
                pass
        _client = AsyncIOMotorClient(
            settings.mongodb_uri,
            serverSelectionTimeoutMS=8000,
        )
        _client_loop = current_loop
    return _client


def get_db() -> AsyncIOMotorDatabase:
    return get_client()[settings.mongodb_db]


def get_collection(name: str):
    return get_db()[name]


import time

_last_health_check_time: float = 0.0
_last_health_status: bool = False


async def check_db_health(force: bool = False) -> bool:
    """Test ping to MongoDB with a short timeout and cached status to prevent endpoint lag."""
    global _last_health_check_time, _last_health_status
    now = time.time()
    cache_ttl = 30.0 if _last_health_status else 15.0
    if not force and (now - _last_health_check_time < cache_ttl):
        return _last_health_status

    try:
        client = get_client()
        await client.admin.command("ping")
        _last_health_status = True
    except Exception as exc:
        if _last_health_status or _last_health_check_time == 0:
            logger.info("MongoDB unavailable (using in-memory fallback): %s", exc)
        _last_health_status = False

    _last_health_check_time = now
    return _last_health_status


async def create_indexes():
    """Create essential indexes for policies, snapshots, analyses, and check events."""
    try:
        db = get_db()
        await db["policies"].create_indexes([
            IndexModel([("canonical_url", ASCENDING)], unique=True),
            IndexModel([("created_at", ASCENDING)]),
            IndexModel([("last_checked_at", ASCENDING)]),
        ])
        await db["snapshots"].create_indexes([
            IndexModel([("policy_id", ASCENDING)]),
            IndexModel([("checked_at", ASCENDING)]),
            IndexModel([("content_hash", ASCENDING)]),
        ])
        await db["analyses"].create_indexes([
            IndexModel([("policy_id", ASCENDING)]),
            IndexModel([("new_snapshot_id", ASCENDING)]),
            IndexModel([("created_at", ASCENDING)]),
        ])
        await db["check_events"].create_indexes([
            IndexModel([("policy_id", ASCENDING)]),
            IndexModel([("checked_at", ASCENDING)]),
        ])
        await db["usage_counters"].create_indexes([
            IndexModel([("period_key", ASCENDING)], unique=True),
        ])
        logger.info("MongoDB indexes verified/created successfully.")
    except Exception as exc:
        logger.warning("Failed to create MongoDB indexes (database may be unreachable): %s", exc)


def close_connection():
    global _client, _client_loop
    if _client is not None:
        _client.close()
        _client = None
        _client_loop = None
