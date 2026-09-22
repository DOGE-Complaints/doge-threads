"""t01 — live marker + skip only if secrets missing (no unconditional skip)."""

from __future__ import annotations

from pathlib import Path

import pytest

from tc05_live_fixtures import secrets_missing, skip_unless_live_secrets

_STUB_PATH = Path(__file__).resolve().parent / "test_providers_ready_01_11.py"


def test_unconditional_skip_stub_removed() -> None:
    text = _STUB_PATH.read_text(encoding="utf-8")
    assert "test_optional_live_integration_not_required" not in text
    assert 'pytest.skip("optional live_integration' not in text


def test_skip_helper_only_when_secrets_absent() -> None:
    assert secrets_missing("", "role") is True
    assert secrets_missing("https://example.supabase.co", "") is True
    assert secrets_missing("https://example.supabase.co", "role") is False


@pytest.mark.live_integration
def test_live_marker_skip_only_if_secrets_absent() -> None:
    url, role = skip_unless_live_secrets()
    assert url.startswith("http")
    assert role
