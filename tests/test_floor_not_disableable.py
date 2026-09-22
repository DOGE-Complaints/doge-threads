from __future__ import annotations

from dataclasses import fields

import pytest

from core.domain.attachment_ref import AttachmentRef
from core.domain.errors import LegalFloorError
from core.domain.knobs import FixedThreadKnobs
from core.infrastructure.in_memory_attachment_ref_store import InMemoryAttachmentRefStore


def test_knobs_have_no_floor_disable_field() -> None:
    names = {item.name for item in fields(FixedThreadKnobs)}
    assert "media_floor_enabled" not in names
    assert "disable_media_floor" not in names
    assert "legal_floor" not in names


def test_empty_allowlist_still_runs_floor() -> None:
    store = InMemoryAttachmentRefStore(
        knobs=FixedThreadKnobs(max_depth=4, media_allowed_types=())
    )
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


def test_permissive_allowlist_cannot_disable_floor() -> None:
    store = InMemoryAttachmentRefStore(
        knobs=FixedThreadKnobs(
            max_depth=4,
            media_allowed_types=("image/png", "image/jpeg", "video/mp4"),
        )
    )
    with pytest.raises(LegalFloorError):
        store.accept_ref(
            AttachmentRef(
                ref_id="blob://cat",
                media_type="image/jpeg",
                comment_id="c1",
                floor_class="catastrophic",
            )
        )
    ok = AttachmentRef(ref_id="blob://ok", media_type="image/png", comment_id="c1")
    assert store.accept_ref(ok) == ok
