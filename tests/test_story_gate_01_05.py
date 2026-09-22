from __future__ import annotations

from dataclasses import fields
from pathlib import Path

from core.api.asgi_app import app
from core.domain.attachment_ref import AttachmentRef


_SRC_ROOT = Path(__file__).resolve().parents[1] / "src"


def test_asgi_still_health_ready_only() -> None:
    paths = sorted(
        path
        for path in (
            getattr(route, "path", None) for route in app.routes if getattr(route, "methods", None)
        )
        if isinstance(path, str)
    )
    assert paths == ["/health", "/ready"]


def test_refs_only_no_byte_store_field() -> None:
    assert "bytes" not in {item.name for item in fields(AttachmentRef)}
    assert "payload" not in {item.name for item in fields(AttachmentRef)}
    assert "blob" not in {item.name for item in fields(AttachmentRef)}


def test_no_pack_loader_and_no_invented_ddl_in_src() -> None:
    hits: list[str] = []
    for path in _SRC_ROOT.rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        if "pack_loader" in text or "load_pack" in text or "CREATE TABLE" in text:
            hits.append(str(path.relative_to(_SRC_ROOT)))
    assert hits == []
