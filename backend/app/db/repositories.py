"""Repository layer for persisting policies, snapshots, analyses, and check events.

Provides high-level async methods with MongoDB Atlas persistence and an automatic
in-memory fallback mode for local development/testing without a live database.
"""
from __future__ import annotations
import logging
import uuid
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from app.db.connection import get_db, check_db_health

logger = logging.getLogger("easyfineprint.repository")


class PolicyRepository:
    """Async repository for policy tracking operations."""

    def __init__(self):
        # In-memory store for dev/testing when MongoDB is unavailable
        self._mem_policies: Dict[str, dict] = {}
        self._mem_snapshots: Dict[str, dict] = {}
        self._mem_analyses: Dict[str, dict] = {}
        self._mem_check_events: Dict[str, dict] = {}
        self._mem_usage: Dict[str, int] = {}

    async def _use_mongo(self) -> bool:
        return await check_db_health()

    # --- Policies ---
    async def get_policy_by_url(self, canonical_url: str) -> Optional[dict]:
        if await self._use_mongo():
            doc = await get_db()["policies"].find_one({"canonical_url": canonical_url})
            if doc:
                doc["id"] = str(doc.get("_id", doc.get("id")))
            return doc
        for p in self._mem_policies.values():
            if p.get("canonical_url") == canonical_url:
                return dict(p)
        return None

    async def get_policy_by_id(self, policy_id: str) -> Optional[dict]:
        if await self._use_mongo():
            doc = await get_db()["policies"].find_one({"_id": policy_id})
            if not doc:
                doc = await get_db()["policies"].find_one({"id": policy_id})
            if doc:
                doc["id"] = str(doc.get("_id", doc.get("id")))
            return doc
        p = self._mem_policies.get(policy_id)
        return dict(p) if p else None

    async def list_policies(self, limit: int = 50) -> List[dict]:
        if await self._use_mongo():
            cursor = get_db()["policies"].find().sort("last_checked_at", -1).limit(limit)
            items = []
            async for doc in cursor:
                doc["id"] = str(doc.get("_id", doc.get("id")))
                items.append(doc)
            return items
        items = sorted(
            list(self._mem_policies.values()),
            key=lambda x: x.get("last_checked_at") or x.get("created_at") or datetime.min,
            reverse=True,
        )
        return [dict(x) for x in items[:limit]]

    async def create_policy(self, url: str, canonical_url: str, title: str) -> dict:
        now = datetime.now(timezone.utc)
        policy_id = f"pol_{uuid.uuid4().hex[:12]}"
        doc = {
            "_id": policy_id,
            "id": policy_id,
            "url": url,
            "canonical_url": canonical_url,
            "title": title,
            "status": "active",
            "created_at": now,
            "last_checked_at": now,
            "latest_snapshot_id": None,
        }
        if await self._use_mongo():
            await get_db()["policies"].insert_one(doc)
        else:
            self._mem_policies[policy_id] = dict(doc)
        return doc

    async def update_policy(self, policy_id: str, updates: dict) -> Optional[dict]:
        if await self._use_mongo():
            await get_db()["policies"].update_one({"_id": policy_id}, {"$set": updates})
            return await self.get_policy_by_id(policy_id)
        if policy_id in self._mem_policies:
            self._mem_policies[policy_id].update(updates)
            return dict(self._mem_policies[policy_id])
        return None

    # --- Snapshots ---
    async def create_snapshot(
        self,
        policy_id: str,
        content_hash: str,
        extracted_text: str,
        extractor: str,
        extraction_status: str,
        source_status_code: int,
        title: str,
    ) -> dict:
        now = datetime.now(timezone.utc)
        snap_id = f"snp_{uuid.uuid4().hex[:12]}"
        doc = {
            "_id": snap_id,
            "id": snap_id,
            "policy_id": policy_id,
            "checked_at": now,
            "content_hash": content_hash,
            "extracted_text": extracted_text,
            "extractor": extractor,
            "extraction_status": extraction_status,
            "source_status_code": source_status_code,
            "title": title,
        }
        if await self._use_mongo():
            await get_db()["snapshots"].insert_one(doc)
        else:
            self._mem_snapshots[snap_id] = dict(doc)

        # Update latest_snapshot_id on policy
        await self.update_policy(policy_id, {
            "latest_snapshot_id": snap_id,
            "last_checked_at": now,
            "title": title,
        })
        return doc

    async def get_snapshot_by_id(self, snapshot_id: str) -> Optional[dict]:
        if await self._use_mongo():
            doc = await get_db()["snapshots"].find_one({"_id": snapshot_id})
            if not doc:
                doc = await get_db()["snapshots"].find_one({"id": snapshot_id})
            if doc:
                doc["id"] = str(doc.get("_id", doc.get("id")))
            return doc
        s = self._mem_snapshots.get(snapshot_id)
        return dict(s) if s else None

    async def list_snapshots_for_policy(self, policy_id: str) -> List[dict]:
        if await self._use_mongo():
            cursor = get_db()["snapshots"].find({"policy_id": policy_id}).sort("checked_at", -1)
            items = []
            async for doc in cursor:
                doc["id"] = str(doc.get("_id", doc.get("id")))
                items.append(doc)
            return items
        items = [s for s in self._mem_snapshots.values() if s.get("policy_id") == policy_id]
        items.sort(key=lambda x: x.get("checked_at", datetime.min), reverse=True)
        return [dict(x) for x in items]

    # --- Analyses ---
    async def create_analysis(
        self,
        policy_id: str,
        analysis_type: str,
        new_snapshot_id: str,
        summary: str,
        findings: list,
        changes: list,
        model_id: str,
        validation_status: str,
        old_snapshot_id: Optional[str] = None,
    ) -> dict:
        now = datetime.now(timezone.utc)
        ana_id = f"ana_{uuid.uuid4().hex[:12]}"
        doc = {
            "_id": ana_id,
            "id": ana_id,
            "policy_id": policy_id,
            "analysis_type": analysis_type,
            "old_snapshot_id": old_snapshot_id,
            "new_snapshot_id": new_snapshot_id,
            "summary": summary,
            "findings": findings,
            "changes": changes,
            "model_id": model_id,
            "created_at": now,
            "validation_status": validation_status,
        }
        if await self._use_mongo():
            await get_db()["analyses"].insert_one(doc)
        else:
            self._mem_analyses[ana_id] = dict(doc)
        return doc

    async def get_latest_analysis_for_policy(self, policy_id: str) -> Optional[dict]:
        if await self._use_mongo():
            doc = await get_db()["analyses"].find_one({"policy_id": policy_id}, sort=[("created_at", -1)])
            if doc:
                doc["id"] = str(doc.get("_id", doc.get("id")))
            return doc
        matches = [a for a in self._mem_analyses.values() if a.get("policy_id") == policy_id]
        if not matches:
            return None
        matches.sort(key=lambda x: x.get("created_at", datetime.min), reverse=True)
        return dict(matches[0])

    # --- Check Events ---
    async def record_check_event(
        self,
        policy_id: str,
        status: str,
        message: str = "",
        old_snapshot_id: Optional[str] = None,
        new_snapshot_id: Optional[str] = None,
    ) -> dict:
        now = datetime.now(timezone.utc)
        evt_id = f"evt_{uuid.uuid4().hex[:12]}"
        doc = {
            "_id": evt_id,
            "id": evt_id,
            "policy_id": policy_id,
            "checked_at": now,
            "status": status,
            "message": message,
            "old_snapshot_id": old_snapshot_id,
            "new_snapshot_id": new_snapshot_id,
        }
        if await self._use_mongo():
            await get_db()["check_events"].insert_one(doc)
        else:
            self._mem_check_events[evt_id] = dict(doc)

        # Update last_checked_at on policy
        await self.update_policy(policy_id, {"last_checked_at": now})
        return doc

    async def list_check_events(self, policy_id: str, limit: int = 30) -> List[dict]:
        if await self._use_mongo():
            cursor = get_db()["check_events"].find({"policy_id": policy_id}).sort("checked_at", -1).limit(limit)
            items = []
            async for doc in cursor:
                doc["id"] = str(doc.get("_id", doc.get("id")))
                items.append(doc)
            return items
        items = [e for e in self._mem_check_events.values() if e.get("policy_id") == policy_id]
        items.sort(key=lambda x: x.get("checked_at", datetime.min), reverse=True)
        return [dict(x) for x in items[:limit]]


repo = PolicyRepository()
