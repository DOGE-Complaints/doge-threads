from __future__ import annotations

import pytest

from core.domain.attachment_ref import AttachmentRef
from core.domain.errors import LegalFloorError, MediaTypeNotAllowedError
from core.domain.knobs import FixedThreadKnobs
from core.infrastructure.in_memory_attachment_ref_store import InMemoryAttachmentRefStore


def test_out_of_policy_media_type_rejected() -> None:
    store = InMemoryAttachmentRefStore(
        knobs=FixedThreadKnobs(max_depth=4, media_allowed_types=("image/png",))
    )
    with pytest.raises(MediaTypeNotAllowedError):
        store.accept_ref(
            AttachmentRef(ref_id="blob://vid", media_type="video/mp4", comment_id="c1")
        )
    assert store.list_refs("c1") == []


def test_allowlist_from_knobs_not_pack_loader() -> None:
    knobs = FixedThreadKnobs(max_depth=4, media_allowed_types=("image/jpeg",))
    store = InMemoryAttachmentRefStore(knobs=knobs)
    ref = AttachmentRef(ref_id="blob://jpg", media_type="image/jpeg", comment_id="c1")
    assert store.accept_ref(ref) == ref
    assert store.knobs.media_allowed_types == ("image/jpeg",)
    assert not hasattr(store, "pack_loader")
    assert not hasattr(store.knobs, "load_pack")


def test_allowlist_is_not_floor() -> None:
    store = InMemoryAttachmentRefStore(
        knobs=FixedThreadKnobs(max_depth=4, media_allowed_types=("image/png",))
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
    with pytest.raises(MediaTypeNotAllowedError):
        store.accept_ref(
            AttachmentRef(ref_id="blob://gif", media_type="image/gif", comment_id="c1")
        )
