"""t01 — domain e2e env contract + skip only if required env absent."""

from __future__ import annotations

from pathlib import Path

import pytest

from tc07_e2e_fixtures import REQUIRED_E2E_ENV, env_missing, skip_unless_e2e_env

_HELPER = Path(__file__).resolve().parent / "tc07_e2e_fixtures.py"


def test_ops_note_lists_required_env_names() -> None:
    text = _HELPER.read_text(encoding="utf-8")
    for name in (
        "IDENTITY_BASE_URL",
        "GATEWAY_BASE_URL",
        "SERVICE_API_TOKEN",
        "SUPABASE_URL",
        "SUPABASE_SERVICE_ROLE",
        "THREADS_E2E_USER_BEARER",
    ):
        assert name in text
    assert "verified USER bearer" in text
    assert REQUIRED_E2E_ENV[0] == "IDENTITY_BASE_URL"


def test_skip_helper_only_when_env_absent() -> None:
    empty = {name: "" for name in REQUIRED_E2E_ENV}
    assert env_missing(empty) == list(REQUIRED_E2E_ENV)
    filled = {name: "x" for name in REQUIRED_E2E_ENV}
    assert env_missing(filled) == []


@pytest.mark.domain_e2e
def test_domain_e2e_skip_only_if_required_env_absent() -> None:
    values = skip_unless_e2e_env()
    assert values["IDENTITY_BASE_URL"].startswith("http")
    assert values["GATEWAY_BASE_URL"].startswith("http")
    assert values["SUPABASE_URL"].startswith("http")
    assert values["THREADS_E2E_USER_BEARER"]
    assert values["THREADS_E2E_ISSUE_ID"]
