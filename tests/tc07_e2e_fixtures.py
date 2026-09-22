"""Domain e2e helpers for STORY-THREADS-TC-07.

Ops note (required env names — no invent secrets):
- IDENTITY_BASE_URL
- GATEWAY_BASE_URL
- SERVICE_API_TOKEN
- SUPABASE_URL
- SUPABASE_SERVICE_ROLE
- THREADS_E2E_USER_BEARER  (verified USER bearer)
- THREADS_E2E_ISSUE_ID     (live issue id fixture)
"""

from __future__ import annotations

import os
from uuid import uuid4

import pytest

from core.config import AppConfig, load_config_from_env
from core.infrastructure.db_supabase import SupabaseDatabase
from core.infrastructure.providers import provide_service_factory
from core.infrastructure.supabase_discussion_mappers import COMMENT_TABLE, THREAD_TABLE
from core.infrastructure.supabase_marks_mappers import MARKS_TABLE
from core.infrastructure.supabase_refs_mappers import REFS_TABLE

REQUIRED_E2E_ENV: tuple[str, ...] = (
    "IDENTITY_BASE_URL",
    "GATEWAY_BASE_URL",
    "SERVICE_API_TOKEN",
    "SUPABASE_URL",
    "SUPABASE_SERVICE_ROLE",
    "THREADS_E2E_USER_BEARER",
    "THREADS_E2E_ISSUE_ID",
)

_CAPTURED: dict[str, str] = {
    name: (os.environ.get(name) or "").strip() for name in REQUIRED_E2E_ENV
}


def env_missing(values: dict[str, str] | None = None) -> list[str]:
    """Names that are empty. Does not invent secret values."""
    source = values if values is not None else live_e2e_env()
    return [name for name in REQUIRED_E2E_ENV if not source.get(name, "").strip()]


def live_e2e_env() -> dict[str, str]:
    out: dict[str, str] = {}
    for name in REQUIRED_E2E_ENV:
        out[name] = _CAPTURED.get(name) or (os.environ.get(name) or "").strip()
    return out


def skip_unless_e2e_env() -> dict[str, str]:
    """Skip only if required env absent (Identity + Gateway + Supabase + verified user)."""
    values = live_e2e_env()
    missing = env_missing(values)
    if missing:
        pytest.skip(
            "required env absent: "
            + ", ".join(missing)
            + " (Identity + Gateway + Supabase + verified user token)"
        )
    return values


def tc07_entity_id() -> str:
    return f"tc07-{uuid4()}"


def make_e2e_factory() -> tuple[object, dict[str, str]]:
    """provide_service_factory supabase + real Me/GW from documented env."""
    values = skip_unless_e2e_env()
    os.environ["SERVICE_API_TOKEN"] = values["SERVICE_API_TOKEN"]
    os.environ["IDENTITY_BASE_URL"] = values["IDENTITY_BASE_URL"]
    os.environ["GATEWAY_BASE_URL"] = values["GATEWAY_BASE_URL"]
    os.environ["SUPABASE_URL"] = values["SUPABASE_URL"]
    os.environ["SUPABASE_SERVICE_ROLE"] = values["SUPABASE_SERVICE_ROLE"]
    config: AppConfig = load_config_from_env(
        {
            "APP_PROFILE": "demo",
            "DB_BACKEND": "supabase",
            "SUPABASE_URL": values["SUPABASE_URL"],
            "SUPABASE_SERVICE_ROLE": values["SUPABASE_SERVICE_ROLE"],
            "IDENTITY_BASE_URL": values["IDENTITY_BASE_URL"],
            "GATEWAY_BASE_URL": values["GATEWAY_BASE_URL"],
        }
    )
    return provide_service_factory(config), values


def cleanup_tc07_prefix(db: SupabaseDatabase, entity_id: str) -> None:
    if not entity_id.startswith("tc07-"):
        raise ValueError(f"refusing cleanup of non-tc07 entity_id: {entity_id!r}")
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
