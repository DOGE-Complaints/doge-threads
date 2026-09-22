"""t03 — U-ATT attachment ref + legal floor edges (offline)."""

from __future__ import annotations

from dataclasses import fields

import pytest

from core.domain.attachment_ref import AttachmentRef
from core.domain.errors import AttachmentRefError, LegalFloorError, MediaTypeNotAllowedError
from core.domain.knobs import FixedThreadKnobs
from core.infrastructure.in_memory_attachment_ref_store import InMemoryAttachmentRefStore


def _store(*, allowed: tuple[str, ...] = ("image/png",)) -> InMemoryAttachmentRefStore:
    return InMemoryAttachmentRefStore(
        knobs=FixedThreadKnobs(max_depth=4, media_allowed_types=allowed)
    )


@pytest.mark.parametrize(
    ("kwargs", "scenario_id"),
    [
        ({"ref_id": "", "media_type": "image/png", "comment_id": "c1"}, "U-ATT-empty-ref"),
        ({"ref_id": "blob://x", "media_type": "", "comment_id": "c1"}, "U-ATT-empty-type"),
        ({"ref_id": "blob://x", "media_type": "image/png", "comment_id": ""}, "U-ATT-empty-comment"),
        (
            {
                "ref_id": "blob://x",
                "media_type": "image/png",
                "comment_id": "c1",
                "floor_class": "unknown-class",
            },
            "U-ATT-bad-floor-class",
        ),
    ],
)
def test_u_att_empty_and_bad_class(kwargs: dict[str, str], scenario_id: str) -> None:
    with pytest.raises(ValueError):
        AttachmentRef(**kwargs)
    assert scenario_id.startswith("U-ATT-")


def test_u_att_allowlist_miss() -> None:
    """U-ATT-allowlist-miss"""
    store = _store(allowed=("image/png",))
    with pytest.raises(MediaTypeNotAllowedError) as exc:
        store.accept_ref(
            AttachmentRef(ref_id="blob://vid", media_type="video/mp4", comment_id="c1")
        )
    assert isinstance(exc.value, AttachmentRefError)
    assert store.list_refs("c1") == []


@pytest.mark.parametrize(
    ("floor_class", "scenario_id"),
    [
        ("csam", "U-ATT-floor-csam"),
        ("catastrophic", "U-ATT-floor-catastrophic"),
    ],
)
def test_u_att_floor_blocked(floor_class: str, scenario_id: str) -> None:
    store = _store()
    with pytest.raises(LegalFloorError) as exc:
        store.accept_ref(
            AttachmentRef(
                ref_id=f"blob://{floor_class}",
                media_type="image/png",
                comment_id="c1",
                floor_class=floor_class,
            )
        )
    assert isinstance(exc.value, AttachmentRefError)
    assert store.list_refs("c1") == []
    assert scenario_id.startswith("U-ATT-floor-")


def test_u_att_floor_ok() -> None:
    """U-ATT-floor-ok"""
    store = _store()
    ref = AttachmentRef(ref_id="blob://ok", media_type="image/png", comment_id="c1")
    assert store.accept_ref(ref) == ref
    assert store.list_refs("c1") == [ref]


def test_u_att_floor_not_disableable() -> None:
    """U-ATT-floor-not-disableable"""
    names = {item.name for item in fields(FixedThreadKnobs)}
    assert "media_floor_enabled" not in names
    assert "disable_media_floor" not in names
    store = _store(allowed=())
    with pytest.raises(LegalFloorError):
        store.accept_ref(
            AttachmentRef(
                ref_id="blob://csam",
                media_type="image/png",
                comment_id="c1",
                floor_class="csam",
            )
        )
    assert store.list_refs("c1") == []
