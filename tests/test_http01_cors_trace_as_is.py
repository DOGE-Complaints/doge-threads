"""t04 — CORS * + x-trace-id as-is; U4 OOS."""

from __future__ import annotations

from pathlib import Path

from fastapi.middleware.cors import CORSMiddleware

from core.api.asgi_app import app

_API_REF = (
    Path(__file__).resolve().parents[1] / "docs" / "runtime-docs" / "api-reference" / "API_REFERENCE.md"
)


def test_cors_middleware_unchanged() -> None:
    cors = next(m for m in app.user_middleware if m.cls is CORSMiddleware)
    assert cors.kwargs["allow_origins"] == ["*"]
    assert cors.kwargs["allow_methods"] == ["GET", "POST", "PUT", "OPTIONS"]
    assert cors.kwargs["allow_headers"] == ["x-trace-id", "authorization"]


def test_cors_documented_u4_oos() -> None:
    text = _API_REF.read_text(encoding="utf-8")
    assert 'allow_origins=["*"]' in text
    assert "x-trace-id" in text
    assert "U4" in text
