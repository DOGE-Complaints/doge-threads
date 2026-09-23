from __future__ import annotations

from asgi_public_paths import CURRENT_PUBLIC_GET_PATHS

from pathlib import Path

from core.api.asgi_app import app
from core.identity import me_client as me_mod
from core.application import write_gate as gate_mod


_SRC_ROOT = Path(__file__).resolve().parents[1] / "src"


def test_asgi_still_health_ready_only() -> None:
    paths = sorted(
        path
        for path in (
            getattr(route, "path", None) for route in app.routes if getattr(route, "methods", None)
        )
        if isinstance(path, str)
    )
    assert paths == CURRENT_PUBLIC_GET_PATHS


def test_no_method_flag_fallback_or_jwt_in_write_path() -> None:
    for module in (me_mod, gate_mod):
        source = Path(module.__file__).read_text(encoding="utf-8")
        assert "phone_verified" not in source
        assert "eid_verified" not in source
        assert "jwt" not in source.lower()
        assert "PyJWT" not in source
    hits: list[str] = []
    for path in (_SRC_ROOT / "core" / "application" / "write_gate.py",):
        text = path.read_text(encoding="utf-8")
        if "phone_verified" in text or "eid_verified" in text:
            hits.append(str(path))
    assert hits == []
