from __future__ import annotations

from dataclasses import dataclass, field

from core.config import AppConfig
from core.infrastructure.db_sqlite import SqliteDatabase
from core.infrastructure.db_supabase import SupabaseDatabase


@dataclass(frozen=True)
class DefaultThreadServiceFactory:
    """Default factory. Product repositories wait REQ01."""

    config: AppConfig
    db_backend: str
    db_ready: bool = True
    db_checks: dict[str, bool] = field(default_factory=dict)
    supabase_db: SupabaseDatabase | None = None
    sqlite_db: SqliteDatabase | None = None
