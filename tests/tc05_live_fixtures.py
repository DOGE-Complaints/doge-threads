"""Env-gated live PostgREST helpers for STORY-THREADS-TC-05.

Skip only if SUPABASE_URL / SUPABASE_SERVICE_ROLE absent. No unconditional skip.
"""

from __future__ import annotations

import os
from uuid import uuid4

import pytest

from core.domain.knobs import FixedThreadKnobs
from core.infrastructure.db_supabase import REQUIRED_READINESS_TABLES, SupabaseDatabase
from core.infrastructure.supabase_attachment_ref_store import SupabaseAttachmentRefStore
from core.infrastructure.supabase_discussion_mappers import COMMENT_TABLE, THREAD_TABLE
from core.infrastructure.supabase_discussion_store import SupabaseDiscussionStore
from core.infrastructure.supabase_marks_mappers import MARKS_TABLE
from core.infrastructure.supabase_reaction_marks_store import SupabaseReactionMarksStore
from core.infrastructure.supabase_refs_mappers import REFS_TABLE

# Capture process env at import (before offline autouse wipe of other tests).
_CAPTURED_URL = (os.environ.get("SUPABASE_URL") or "").strip()
_CAPTURED_ROLE = (os.environ.get("SUPABASE_SERVICE_ROLE") or "").strip()


def secrets_missing(url: str, role: str) -> bool:
    """True when either live secret is empty."""
    return not url.strip() or not role.strip()


def live_secret_pair() -> tuple[str, str]:
    url = _CAPTURED_URL or (os.environ.get("SUPABASE_URL") or "").strip()
    role = _CAPTURED_ROLE or (os.environ.get("SUPABASE_SERVICE_ROLE") or "").strip()
    return url, role


def skip_unless_live_secrets() -> tuple[str, str]:
    """Skip only if SUPABASE_URL / SUPABASE_SERVICE_ROLE absent."""
    url, role = live_secret_pair()
    if secrets_missing(url, role):
        pytest.skip("SUPABASE_URL / SUPABASE_SERVICE_ROLE absent")
    return url, role


def tc05_entity_id() -> str:
    """Isolation prefix lock: tc05-{uuid}."""
    return f"tc05-{uuid4()}"


def live_knobs() -> FixedThreadKnobs:
    return FixedThreadKnobs(max_depth=3, max_reactions_per_actor=3)


def live_db() -> SupabaseDatabase:
    url, role = skip_unless_live_secrets()
    return SupabaseDatabase.from_http(supabase_url=url, service_role_key=role)


def live_stores(
    db: SupabaseDatabase,
) -> tuple[SupabaseDiscussionStore, SupabaseReactionMarksStore, SupabaseAttachmentRefStore]:
    knobs = live_knobs()
    return (
        SupabaseDiscussionStore(db=db, knobs=knobs),
        SupabaseReactionMarksStore(db=db, knobs=knobs),
        SupabaseAttachmentRefStore(db=db, knobs=knobs),
    )


def cleanup_tc05_prefix(db: SupabaseDatabase, entity_id: str) -> None:
    """Optional delete of rows isolated by tc05-{uuid} entity_id (L-PG-CLN)."""
    if not entity_id.startswith("tc05-"):
        raise ValueError(f"refusing cleanup of non-tc05 entity_id: {entity_id!r}")
    comments = db._request(
        method="GET",
        path=f"/rest/v1/{COMMENT_TABLE}",
        params={"select": "comment_id", "entity_id": f"eq.{entity_id}"},
    )
    comment_ids: list[str] = []
    if isinstance(comments, list):
        comment_ids = [
            str(row["comment_id"])
            for row in comments
            if isinstance(row, dict) and row.get("comment_id")
        ]
    for comment_id in comment_ids:
        db._request(
            method="DELETE",
            path=f"/rest/v1/{REFS_TABLE}",
            params={"comment_id": f"eq.{comment_id}"},
        )
    db._request(
        method="DELETE",
        path=f"/rest/v1/{MARKS_TABLE}",
        params={"entity_id": f"eq.{entity_id}"},
    )
    db._request(
        method="DELETE",
        path=f"/rest/v1/{COMMENT_TABLE}",
        params={"entity_id": f"eq.{entity_id}"},
    )
    db._request(
        method="DELETE",
        path=f"/rest/v1/{THREAD_TABLE}",
        params={"entity_id": f"eq.{entity_id}"},
    )


__all__ = [
    "REQUIRED_READINESS_TABLES",
    "cleanup_tc05_prefix",
    "live_db",
    "live_knobs",
    "live_secret_pair",
    "live_stores",
    "secrets_missing",
    "skip_unless_live_secrets",
    "tc05_entity_id",
]
