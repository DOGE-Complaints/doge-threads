from __future__ import annotations

from dataclasses import dataclass, field
from functools import lru_cache
from os import environ

from core.config import AppConfig, load_config_from_env
from core.config.env_file import merge_dotenv_from_cwd


@dataclass(frozen=True)
class ApiDependencies:
    """DI shell for HTTP handlers. Persistence/auth clients stay stubs until 00-04/00-05."""

    config: AppConfig
    db_backend: str = "in_memory"
    db_ready: bool = True
    db_checks: dict[str, bool] = field(default_factory=dict)


@lru_cache(maxsize=1)
def build_api_dependencies() -> ApiDependencies:
    """Construct the cached DI container from env (in_memory needs no Supabase)."""
    priority = dict(environ)
    source = dict(priority)
    merge_dotenv_from_cwd(source, priority=priority)
    config = load_config_from_env(source)
    db_backend = config.db_backend
    if db_backend == "in_memory":
        db_ready = True
        db_checks: dict[str, bool] = {"in_memory": True}
    else:
        # No persistence providers in 00-03; later stories fill supabase/sqlite checks.
        db_ready = False
        db_checks = {}
    return ApiDependencies(
        config=config,
        db_backend=db_backend,
        db_ready=db_ready,
        db_checks=db_checks,
    )
