"""t01–t02 — HTTP-06 OpenAPI Close: docs match Closed inventory."""

from __future__ import annotations

from pathlib import Path

from asgi_public_paths import CLOSED_HTTP_INVENTORY, listed_asgi_method_paths
from core.api.asgi_app import app

_ROOT = Path(__file__).resolve().parents[1]
_WORKSPACE = _ROOT.parent
_OPENAPI = _ROOT / "docs" / "runtime-docs" / "api-reference" / "openapi.yaml"
_API_REF = _ROOT / "docs" / "runtime-docs" / "api-reference" / "API_REFERENCE.md"
_ADMIN = (
    _WORKSPACE
    / "spa-app"
    / "docs"
    / "tasks"
    / "backlog-stories"
    / "threads-feed"
    / "ADMIN-THR-04-api-requirements.md"
)
_FE_REQ = (
    _WORKSPACE
    / "spa-app"
    / "docs"
    / "tasks"
    / "backlog-stories"
    / "threads-feed"
    / "STORY-SPA-THR-api-requirements.md"
)


def test_asgi_matches_closed_inventory() -> None:
    assert listed_asgi_method_paths(app) == CLOSED_HTTP_INVENTORY


def test_openapi_documents_closed_inventory() -> None:
    text = _OPENAPI.read_text(encoding="utf-8")
    for method, path in CLOSED_HTTP_INVENTORY:
        assert path in text
        assert method.lower() in text
    assert "/threads/by-issue" not in text


def test_api_reference_documents_closed_inventory() -> None:
    text = _API_REF.read_text(encoding="utf-8")
    for _method, path in CLOSED_HTTP_INVENTORY:
        assert path in text
    assert "/threads/by-issue" not in text
    assert "ThreadsSocialClient" in text
    assert "separate spa wave" in text


def test_sibling_docs_mark_closed_and_defer_spa_wire() -> None:
    admin = _ADMIN.read_text(encoding="utf-8")
    fe_req = _FE_REQ.read_text(encoding="utf-8")
    assert "**Closed**" in admin
    assert "separate spa wave" in admin
    assert "04-spa-consumer-handoff.md" in admin
    assert "✅ Closed" in fe_req
    assert "separate spa wave" in fe_req
    assert "04-spa-consumer-handoff.md" in fe_req
