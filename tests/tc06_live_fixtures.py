"""Env-gated live orchestrator helpers for STORY-THREADS-TC-06.

Factory supabase + stub Me/Gateway. Skip only if secrets absent.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from unittest.mock import MagicMock
from uuid import uuid4

from core.application.write_gate import IdentityVerifiedWriteGate
from core.application.write_orchestrator import ThreadWriteOrchestrator
from core.config import AppConfig, load_config_from_env
from core.domain.knobs import FixedThreadKnobs
from core.infrastructure.db_supabase import SupabaseDatabase
from core.infrastructure.providers import provide_service_factory
from core.infrastructure.supabase_attachment_ref_store import SupabaseAttachmentRefStore
from core.infrastructure.supabase_discussion_mappers import COMMENT_TABLE, THREAD_TABLE
from core.infrastructure.supabase_discussion_store import SupabaseDiscussionStore
from core.infrastructure.supabase_marks_mappers import MARKS_TABLE
from core.infrastructure.supabase_reaction_marks_store import SupabaseReactionMarksStore
from core.infrastructure.supabase_refs_mappers import REFS_TABLE
from tc05_live_fixtures import live_secret_pair, skip_unless_live_secrets
from threadcontext_fixtures import stub_gateway_client
from write_orchestrator_fixtures import patch_gateway


@dataclass
class LiveOrchHarness:
    factory: Any
    orchestrator: ThreadWriteOrchestrator
    discussion: SupabaseDiscussionStore
    reactions: SupabaseReactionMarksStore
    attachments: SupabaseAttachmentRefStore
    mock_http: MagicMock
    me: MagicMock
    db: SupabaseDatabase
    config: AppConfig


def tc06_entity_id() -> str:
    """Isolation prefix: tc06-{uuid}."""
    return f"tc06-{uuid4()}"


def live_supabase_config() -> AppConfig:
    """Factory config: DB_BACKEND=supabase + captured live secrets."""
    url, role = skip_unless_live_secrets()
    return load_config_from_env(
        {
            "APP_PROFILE": "demo",
            "DB_BACKEND": "supabase",
            "SUPABASE_URL": url,
            "SUPABASE_SERVICE_ROLE": role,
        }
    )


def attach_stub_siblings(orchestrator: ThreadWriteOrchestrator) -> tuple[MagicMock, MagicMock]:
    """Replace live factory Me/Gateway with stubs (TC-07 owns real siblings)."""
    me = MagicMock()
    me.fetch_me.return_value = {"data": {"identity_verified": True}}
    gateway, mock_http = stub_gateway_client()
    orchestrator._gateway = gateway
    orchestrator._gate = IdentityVerifiedWriteGate(me)
    return mock_http, me


def make_live_orch_harness() -> LiveOrchHarness:
    """provide_service_factory supabase + stub Me/GW; knobs from factory (fixed)."""
    config = live_supabase_config()
    factory = provide_service_factory(config)
    orchestrator = factory.write_orchestrator
    assert isinstance(orchestrator, ThreadWriteOrchestrator)
    mock_http, me = attach_stub_siblings(orchestrator)
    db = factory.supabase_db
    if db is None:
        raise AssertionError("factory supabase_db missing after live secrets")
    return LiveOrchHarness(
        factory=factory,
        orchestrator=orchestrator,
        discussion=factory.discussion_store,  # type: ignore[arg-type]
        reactions=orchestrator._reactions,  # type: ignore[arg-type]
        attachments=orchestrator._attachments,  # type: ignore[arg-type]
        mock_http=mock_http,
        me=me,
        db=db,
        config=config,
    )


def new_reader_stores() -> tuple[
    SupabaseDiscussionStore,
    SupabaseReactionMarksStore,
    SupabaseAttachmentRefStore,
    SupabaseDatabase,
]:
    """Second SupabaseDatabase / store instance (new client)."""
    url, role = live_secret_pair()
    db = SupabaseDatabase.from_http(supabase_url=url, service_role_key=role)
    knobs = FixedThreadKnobs(max_depth=8)
    return (
        SupabaseDiscussionStore(db=db, knobs=knobs),
        SupabaseReactionMarksStore(db=db, knobs=knobs),
        SupabaseAttachmentRefStore(db=db, knobs=knobs),
        db,
    )


def cleanup_tc06_prefix(db: SupabaseDatabase, entity_id: str) -> None:
    """Delete rows isolated by tc06-{uuid} entity_id."""
    if not entity_id.startswith("tc06-"):
        raise ValueError(f"refusing cleanup of non-tc06 entity_id: {entity_id!r}")
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
    "LiveOrchHarness",
    "attach_stub_siblings",
    "cleanup_tc06_prefix",
    "live_supabase_config",
    "make_live_orch_harness",
    "new_reader_stores",
    "patch_gateway",
    "skip_unless_live_secrets",
    "tc06_entity_id",
]
