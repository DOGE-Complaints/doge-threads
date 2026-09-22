from __future__ import annotations

from dataclasses import dataclass, field

from core.config import AppConfig
from core.domain.ports import DiscussionStore, ThreadKnobs
from core.infrastructure.db_sqlite import SqliteDatabase
from core.infrastructure.db_supabase import SupabaseDatabase


@dataclass(frozen=True)
class DefaultThreadServiceFactory:
    """Default factory. Discussion store is in_memory for REQ01 proofs."""

    config: AppConfig
    db_backend: str
    discussion_store: DiscussionStore
    thread_knobs: ThreadKnobs
    db_ready: bool = True
    db_checks: dict[str, bool] = field(default_factory=dict)
    supabase_db: SupabaseDatabase | None = None
    sqlite_db: SqliteDatabase | None = None
