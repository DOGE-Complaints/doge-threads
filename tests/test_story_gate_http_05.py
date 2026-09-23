"""t04 — STORY-THREADS-HTTP-05 story gate: POST attachment-refs."""

from __future__ import annotations

from asgi_public_paths import CURRENT_PUBLIC_GET_PATHS, listed_asgi_paths
from core.api.asgi_app import app


def test_post_attachment_refs_route_registered() -> None:
    paths = listed_asgi_paths(app)
    assert paths == CURRENT_PUBLIC_GET_PATHS
    assert "/threads/issues/{issue_id}/attachment-refs" in paths
