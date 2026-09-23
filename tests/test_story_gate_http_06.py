"""t04 — STORY-THREADS-HTTP-06 story gate: OpenAPI Close inventory."""

from __future__ import annotations

from asgi_public_paths import CLOSED_HTTP_INVENTORY, listed_asgi_method_paths
from core.api.asgi_app import app


def test_closed_inventory_registered() -> None:
    assert listed_asgi_method_paths(app) == CLOSED_HTTP_INVENTORY
