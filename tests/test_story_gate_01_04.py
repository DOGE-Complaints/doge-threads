from __future__ import annotations

from pathlib import Path

from core.api.asgi_app import app
from core.domain.reaction_catalog import CATALOG_REACTION_IDS, REACTION_LAYER


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


def test_catalog_ids_not_renamed() -> None:
    assert "acknowledge" in CATALOG_REACTION_IDS
    assert "agree" in CATALOG_REACTION_IDS
    assert "disagree" in CATALOG_REACTION_IDS
    assert "off_topic" in CATALOG_REACTION_IDS
    assert REACTION_LAYER["agree"] == "epistemic"
    assert REACTION_LAYER["off_topic"] == "moderation"
    assert "like" not in CATALOG_REACTION_IDS


def test_no_voice_weight_application_in_src() -> None:
    hits: list[str] = []
    for path in _SRC_ROOT.rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        if "voice_weight" in text or "min_overlap_to_use" in text:
            hits.append(str(path.relative_to(_SRC_ROOT)))
    assert hits == []
