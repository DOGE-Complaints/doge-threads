from __future__ import annotations

from pathlib import Path

from core.api.asgi_app import app

_CIVIC_NAMES = frozenset(
    {
        "intake",
        "cluster",
        "geo",
        "schema-packs",
        "schema_packs",
        "promotion",
    }
)
_SRC_ROOT = Path(__file__).resolve().parents[1] / "src"
_PRODUCT_PATH_MARKERS = ("thread", "reaction", "comment")


def test_no_civic_modules_under_src() -> None:
    found = sorted(
        str(path.relative_to(_SRC_ROOT))
        for path in _SRC_ROOT.rglob("*")
        if path.is_dir() and path.name in _CIVIC_NAMES
    )
    assert found == []


def test_asgi_has_no_public_thread_product_routes() -> None:
    paths = sorted(
        path
        for path in (
            getattr(route, "path", None) for route in app.routes if getattr(route, "methods", None)
        )
        if isinstance(path, str)
    )
    assert paths == ["/health", "/ready"]
    assert not any(
        any(marker in path for marker in _PRODUCT_PATH_MARKERS) for path in paths
    )
