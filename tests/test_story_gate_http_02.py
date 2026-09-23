"""t06 — STORY-THREADS-HTTP-02 story gate: both GETs, T1, U1, ThreadKey.node."""

from __future__ import annotations

from asgi_public_paths import CURRENT_PUBLIC_GET_PATHS, listed_asgi_paths
from core.api.asgi_app import app
from core.api.thread_key_builder import build_issue_thread_key


def test_both_http02_routes_registered() -> None:
    paths = listed_asgi_paths(app)
    assert paths == CURRENT_PUBLIC_GET_PATHS
    assert "/threads/knobs" in paths
    assert "/threads/issues/{issue_id}" in paths


def test_thread_key_builder_uses_civic_issue_and_schema_id() -> None:
    key = build_issue_thread_key(issue_id="civic-1", schema_id="node-a")
    assert key.node == "node-a"
    assert key.entity_type == "Issue"
    assert key.entity_id == "civic-1"
