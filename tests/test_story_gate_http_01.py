"""t05 — STORY-THREADS-HTTP-01 story gate: transport AC, no product paths."""

from __future__ import annotations

from pathlib import Path

from core.api.asgi_app import app, product_write_bearer
from core.config import ENV_SCHEMA

_ROOT = Path(__file__).resolve().parents[1]
_ASGI = _ROOT / "src" / "core" / "api" / "asgi_app.py"
_EXAMPLE = _ROOT / "example.env"
_PRODUCT_PREFIXES = ("/threads", "/comment", "/reaction", "/attachment")


def test_schema_and_example_env_have_dogestonia_keys() -> None:
    names = {spec.name for spec in ENV_SCHEMA}
    assert {"DOGESTONIA_SCHEMA_ID", "DOGESTONIA_SCHEMA_VERSION"} <= names
    env = _EXAMPLE.read_text(encoding="utf-8")
    assert "DOGESTONIA_SCHEMA_ID=" in env
    assert "DOGESTONIA_SCHEMA_VERSION=" in env


def test_named_product_write_bearer_exists() -> None:
    assert callable(product_write_bearer)
    assert product_write_bearer.__name__ == "product_write_bearer"


def test_no_product_social_routes() -> None:
    paths = sorted(
        path
        for path in (
            getattr(route, "path", None) for route in app.routes if getattr(route, "methods", None)
        )
        if isinstance(path, str)
    )
    assert paths == ["/health", "/ready"]
    asgi = _ASGI.read_text(encoding="utf-8")
    for prefix in _PRODUCT_PREFIXES:
        assert f'@app.get("{prefix}' not in asgi
        assert f'@app.post("{prefix}' not in asgi
        assert f'@app.put("{prefix}' not in asgi
