"""t05 — STORY-THREADS-HTTP-01 story gate: transport AC, no product paths."""

from __future__ import annotations

from asgi_public_paths import CURRENT_PUBLIC_GET_PATHS

from pathlib import Path

from core.api.asgi_app import app, product_write_bearer
from core.config import ENV_SCHEMA

_ROOT = Path(__file__).resolve().parents[1]
_ASGI = _ROOT / "src" / "core" / "api" / "asgi_app.py"
_EXAMPLE = _ROOT / "example.env"
_WRITE_PREFIXES = ("/comment", "/reaction", "/attachment")


def test_schema_and_example_env_have_dogestonia_keys() -> None:
    names = {spec.name for spec in ENV_SCHEMA}
    assert {"DOGESTONIA_SCHEMA_ID", "DOGESTONIA_SCHEMA_VERSION"} <= names
    env = _EXAMPLE.read_text(encoding="utf-8")
    assert "DOGESTONIA_SCHEMA_ID=" in env
    assert "DOGESTONIA_SCHEMA_VERSION=" in env


def test_named_product_write_bearer_exists() -> None:
    assert callable(product_write_bearer)
    assert product_write_bearer.__name__ == "product_write_bearer"


def test_no_product_write_routes_yet() -> None:
    paths = sorted(
        path
        for path in (
            getattr(route, "path", None) for route in app.routes if getattr(route, "methods", None)
        )
        if isinstance(path, str)
    )
    assert paths == CURRENT_PUBLIC_GET_PATHS
    asgi = _ASGI.read_text(encoding="utf-8")
    for prefix in _WRITE_PREFIXES:
        assert f'@app.get("{prefix}' not in asgi
        assert f'@app.post("{prefix}' not in asgi
        assert f'@app.put("{prefix}' not in asgi
    assert '@app.post("/threads/issues/{issue_id}/comments")' in asgi
    assert '@app.put("/threads/issues/{issue_id}/reactions")' in asgi
    assert '@app.put("/threads/by-issue' not in asgi
    assert '@app.post("/threads/issues/{issue_id}/attachment-refs")' in asgi
    assert "@app.post(\"/threads/issues/{issue_id}/attachment-refs/bytes" not in asgi
