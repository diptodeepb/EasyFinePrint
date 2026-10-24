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


import re

def _sanitize_string_id(val: Any, field_name: str = "id") -> str:
    """Strictly sanitize identifier strings, rejecting null bytes, dicts, or NoSQL operator injection."""
    if not isinstance(val, str):
        raise ValueError(f"Invalid {field_name}: expected string, got {type(val).__name__}")
    clean = val.strip()
    if not clean or len(clean) > 128:
        raise ValueError(f"Invalid {field_name}: invalid length")
    if not re.match(r"^[a-zA-Z0-9_\-\.:/]+$", clean):
        raise ValueError(f"Invalid {field_name}: illegal characters detected")
    return clean


def _normalize_doc(doc: Optional[dict]) -> Optional[dict]:
    if not doc:
        return None
    res = dict(doc)
    if "_id" in res:
        res["id"] = str(res.get("_id", res.get("id")))
    for k, v in res.items():
        if isinstance(v, datetime) and v.tzinfo is None:
            res[k] = v.replace(tzinfo=timezone.utc)
    return res


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
    async def get_policy_by_url(self, url: str) -> Optional[dict]:
        clean = url.strip()
        alt = clean[:-1] if clean.endswith("/") else clean + "/"
        candidates = list({clean, alt})
        if await self._use_mongo():
            doc = await get_db()["policies"].find_one({
                "$or": [
                    {"canonical_url": {"$in": candidates}},
                    {"url": {"$in": candidates}},
                ]
            })
            return _normalize_doc(doc)
        for p in self._mem_policies.values():
            if p.get("canonical_url") in candidates or p.get("url") in candidates:
                return _normalize_doc(p)
        return None

    async def get_policy_by_id(self, policy_id: str) -> Optional[dict]:
        clean_id = _sanitize_string_id(policy_id, "policy_id")
        if await self._use_mongo():
            doc = await get_db()["policies"].find_one({"_id": {"$eq": clean_id}})
            if not doc:
                doc = await get_db()["policies"].find_one({"id": {"$eq": clean_id}})
            return _normalize_doc(doc)
        p = self._mem_policies.get(clean_id)
        return _normalize_doc(p)

    async def list_policies(self, limit: int = 50) -> List[dict]:
        safe_limit = min(max(1, int(limit)), 100)
        if await self._use_mongo():
            cursor = get_db()["policies"].find().sort("last_checked_at", -1).limit(safe_limit)
            items = []
            async for doc in cursor:
                items.append(_normalize_doc(doc))
            return items
        items = sorted(
            list(self._mem_policies.values()),
            key=lambda x: x.get("last_checked_at") or x.get("created_at") or datetime.min,
            reverse=True,
        )
        return [_normalize_doc(x) for x in items[:limit]]

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
        clean_id = _sanitize_string_id(policy_id, "policy_id")
        if await self._use_mongo():
            await get_db()["policies"].update_one({"_id": {"$eq": clean_id}}, {"$set": updates})
            return await self.get_policy_by_id(clean_id)
        if clean_id in self._mem_policies:
            self._mem_policies[clean_id].update(updates)
            return dict(self._mem_policies[clean_id])
        return None

    async def delete_policy(self, policy_id: str) -> bool:
        """Permanently delete a policy and all associated snapshots, analyses, and check events."""
        clean_id = _sanitize_string_id(policy_id, "policy_id")
        if await self._use_mongo():
            db = get_db()
            res = await db["policies"].delete_one({"_id": {"$eq": clean_id}})
            await db["snapshots"].delete_many({"policy_id": {"$eq": clean_id}})
            await db["analyses"].delete_many({"policy_id": {"$eq": clean_id}})
            await db["check_events"].delete_many({"policy_id": {"$eq": clean_id}})
            return res.deleted_count > 0
        else:
            if clean_id in self._mem_policies:
                del self._mem_policies[clean_id]
                self._mem_snapshots = {k: v for k, v in self._mem_snapshots.items() if v.get("policy_id") != clean_id}
                self._mem_analyses = {k: v for k, v in self._mem_analyses.items() if v.get("policy_id") != clean_id}
                self._mem_check_events = {k: v for k, v in self._mem_check_events.items() if v.get("policy_id") != clean_id}
                return True
            return False

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
        clean_id = _sanitize_string_id(snapshot_id, "snapshot_id")
        if await self._use_mongo():
            doc = await get_db()["snapshots"].find_one({"_id": {"$eq": clean_id}})
            if not doc:
                doc = await get_db()["snapshots"].find_one({"id": {"$eq": clean_id}})
            return _normalize_doc(doc)
        s = self._mem_snapshots.get(clean_id)
        return _normalize_doc(s)

    async def list_snapshots_for_policy(self, policy_id: str) -> List[dict]:
        clean_id = _sanitize_string_id(policy_id, "policy_id")
        if await self._use_mongo():
            cursor = get_db()["snapshots"].find({"policy_id": {"$eq": clean_id}}).sort("checked_at", -1)
            items = []
            async for doc in cursor:
                items.append(_normalize_doc(doc))
            return items
        items = [s for s in self._mem_snapshots.values() if s.get("policy_id") == clean_id]
        items.sort(key=lambda x: x.get("checked_at", datetime.min), reverse=True)
        return [_normalize_doc(x) for x in items]

    async def get_latest_snapshot_for_policy(self, policy_id: str) -> Optional[dict]:
        """Fetch newest snapshot for a policy, checking latest_snapshot_id or sorting by checked_at."""
        clean_id = _sanitize_string_id(policy_id, "policy_id")
        policy = await self.get_policy_by_id(clean_id)
        if policy and policy.get("latest_snapshot_id"):
            snap = await self.get_snapshot_by_id(policy["latest_snapshot_id"])
            if snap:
                return snap
        snaps = await self.list_snapshots_for_policy(clean_id)
        return snaps[0] if snaps else None

    async def get_snapshot_by_hash(self, content_hash: str) -> Optional[dict]:
        """Find an existing snapshot matching the exact content hash."""
        clean_hash = _sanitize_string_id(content_hash, "content_hash")
        if await self._use_mongo():
            doc = await get_db()["snapshots"].find_one({"content_hash": {"$eq": clean_hash}})
            return _normalize_doc(doc)
        for s in self._mem_snapshots.values():
            if s.get("content_hash") == clean_hash:
                return _normalize_doc(s)
        return None

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
        risk_score: Optional[int] = None,
        risk_level: Optional[str] = None,
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
            "risk_score": risk_score,
            "risk_level": risk_level,
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
        return _normalize_doc(doc)

    async def get_latest_analysis_for_policy(self, policy_id: str) -> Optional[dict]:
        clean_id = _sanitize_string_id(policy_id, "policy_id")
        if await self._use_mongo():
            doc = await get_db()["analyses"].find_one({"policy_id": {"$eq": clean_id}}, sort=[("created_at", -1)])
            return _normalize_doc(doc)
        matches = [a for a in self._mem_analyses.values() if a.get("policy_id") == clean_id]
        if not matches:
            return None
        matches.sort(key=lambda x: x.get("created_at", datetime.min), reverse=True)
        return _normalize_doc(matches[0])

    # --- Check Events ---
    async def record_check_event(
        self,
        policy_id: str,
        status: str,
        message: str = "",
        old_snapshot_id: Optional[str] = None,
        new_snapshot_id: Optional[str] = None,
    ) -> dict:
        clean_policy_id = _sanitize_string_id(policy_id, "policy_id")
        clean_old_snap = _sanitize_string_id(old_snapshot_id, "old_snapshot_id") if old_snapshot_id else None
        clean_new_snap = _sanitize_string_id(new_snapshot_id, "new_snapshot_id") if new_snapshot_id else None
        now = datetime.now(timezone.utc)
        evt_id = f"evt_{uuid.uuid4().hex[:12]}"
        doc = {
            "_id": evt_id,
            "id": evt_id,
            "policy_id": clean_policy_id,
            "checked_at": now,
            "status": status,
            "message": message,
            "old_snapshot_id": clean_old_snap,
            "new_snapshot_id": clean_new_snap,
        }
        if await self._use_mongo():
            await get_db()["check_events"].insert_one(doc)
        else:
            self._mem_check_events[evt_id] = dict(doc)

        # Update last_checked_at on policy
        await self.update_policy(clean_policy_id, {"last_checked_at": now})
        return _normalize_doc(doc)

    async def list_check_events(self, policy_id: str, limit: int = 30) -> List[dict]:
        clean_id = _sanitize_string_id(policy_id, "policy_id")
        safe_limit = min(max(1, int(limit)), 100)
        if await self._use_mongo():
            cursor = get_db()["check_events"].find({"policy_id": {"$eq": clean_id}}).sort("checked_at", -1).limit(safe_limit)
            items = []
            async for doc in cursor:
                items.append(_normalize_doc(doc))
            return items
        items = [e for e in self._mem_check_events.values() if e.get("policy_id") == clean_id]
        items.sort(key=lambda x: x.get("checked_at", datetime.min), reverse=True)
        return [_normalize_doc(x) for x in items[:safe_limit]]

    async def clear_all_data(self) -> dict:
        """Wipe all documents across database collections for a clean state."""
        counts = {}
        if await self._use_mongo():
            db = get_db()
            for col in ["policies", "snapshots", "analyses", "check_events", "usage_counters"]:
                res = await db[col].delete_many({})
                counts[col] = res.deleted_count
        self._mem_policies.clear()
        self._mem_snapshots.clear()
        self._mem_analyses.clear()
        self._mem_check_events.clear()
        self._mem_usage.clear()
        return counts


repo = PolicyRepository()
