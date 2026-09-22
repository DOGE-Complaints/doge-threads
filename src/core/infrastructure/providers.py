from __future__ import annotations

import logging
from os import environ

from core.application.factory import ThreadServiceFactory
from core.application.write_gate import IdentityVerifiedWriteGate
from core.application.write_orchestrator import ThreadWriteOrchestrator
from core.config import AppConfig, load_config_from_env
from core.config.env_file import merge_dotenv_from_cwd
from core.domain.knobs import FixedThreadKnobs
from core.gateway.client import build_gateway_client_from_config
from core.identity.me_client import build_identity_me_from_config
from core.infrastructure.db_sqlite import SqliteDatabase
from core.infrastructure.db_supabase import SupabaseDatabase
from core.infrastructure.in_memory_attachment_ref_store import InMemoryAttachmentRefStore
from core.infrastructure.in_memory_discussion_store import InMemoryDiscussionStore
from core.infrastructure.in_memory_reaction_marks_store import InMemoryReactionMarksStore
from core.infrastructure.service_factory import DefaultThreadServiceFactory
from core.infrastructure.supabase_attachment_ref_store import SupabaseAttachmentRefStore
from core.infrastructure.supabase_discussion_store import SupabaseDiscussionStore
from core.infrastructure.supabase_reaction_marks_store import SupabaseReactionMarksStore

logger = logging.getLogger(__name__)


def provide_app_config() -> AppConfig:
    priority = dict(environ)
    source = dict(priority)
    merge_dotenv_from_cwd(source, priority=priority)
    return load_config_from_env(source)


def provide_service_factory(config: AppConfig | None = None) -> ThreadServiceFactory:
    """Select in_memory | sqlite | supabase. in_memory needs no remote project."""
    resolved_config = config or provide_app_config()
    backend = resolved_config.db_backend
    logger.info(
        "factory.persistence_backend_selected backend=%s",
        backend,
        extra={"backend": backend, "stage": "infrastructure.providers"},
    )
    supabase_db: SupabaseDatabase | None = None
    sqlite_db: SqliteDatabase | None = None
    db_ready = True
    db_checks: dict[str, bool] = {}

    if backend == "in_memory":
        db_ready = True
        db_checks = {"in_memory": True}
    elif backend == "sqlite":
        sqlite_db = SqliteDatabase.from_memory()
        db_checks = {"connectivity": sqlite_db.healthcheck()}
        db_ready = db_checks["connectivity"]
    elif backend == "supabase":
        has_credentials = bool(
            resolved_config.supabase_url and resolved_config.supabase_service_role
        )
        if has_credentials:
            supabase_db = SupabaseDatabase.from_http(
                supabase_url=resolved_config.supabase_url or "",
                service_role_key=resolved_config.supabase_service_role or "",
            )
            db_checks = {
                "credentials": True,
                "tables": supabase_db.required_tables_ready(),
            }
            db_ready = all(db_checks.values())
        else:
            db_ready = False
            db_checks = {"credentials": False}
    else:
        db_ready = False
        db_checks = {}

    thread_knobs = FixedThreadKnobs(max_depth=8)
    if backend == "supabase" and supabase_db is not None:
        discussion_store = SupabaseDiscussionStore(db=supabase_db, knobs=thread_knobs)
        reaction_store = SupabaseReactionMarksStore(db=supabase_db, knobs=thread_knobs)
        attachment_store = SupabaseAttachmentRefStore(db=supabase_db, knobs=thread_knobs)
    else:
        discussion_store = InMemoryDiscussionStore(knobs=thread_knobs)
        reaction_store = InMemoryReactionMarksStore(knobs=thread_knobs)
        attachment_store = InMemoryAttachmentRefStore(knobs=thread_knobs)
    write_orchestrator = ThreadWriteOrchestrator(
        gateway=build_gateway_client_from_config(resolved_config),
        write_gate=IdentityVerifiedWriteGate(
            build_identity_me_from_config(resolved_config)
        ),
        discussion_store=discussion_store,
        reaction_store=reaction_store,
        attachment_store=attachment_store,
    )
    return DefaultThreadServiceFactory(
        config=resolved_config,
        db_backend=backend,
        discussion_store=discussion_store,
        thread_knobs=thread_knobs,
        write_orchestrator=write_orchestrator,
        db_ready=db_ready,
        db_checks=db_checks,
        supabase_db=supabase_db,
        sqlite_db=sqlite_db,
    )
