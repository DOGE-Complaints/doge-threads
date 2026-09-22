from __future__ import annotations

from dataclasses import fields

from core.domain.attachment_ref import AttachmentRef
from core.domain.knobs import FixedThreadKnobs
from core.domain.ports import AttachmentRefStore
from core.infrastructure.in_memory_attachment_ref_store import InMemoryAttachmentRefStore


def _store() -> InMemoryAttachmentRefStore:
    return InMemoryAttachmentRefStore(
        knobs=FixedThreadKnobs(max_depth=4, media_allowed_types=("image/png",))
    )


def test_persist_reference_only() -> None:
    store: AttachmentRefStore = _store()
    ref = AttachmentRef(ref_id="blob://a1", media_type="image/png", comment_id="c1")
    stored = store.accept_ref(ref)
    assert stored == ref
    assert store.list_refs("c1") == [ref]
    assert not hasattr(stored, "bytes")
    assert "bytes" not in {item.name for item in fields(AttachmentRef)}


def test_ref_has_media_type_for_policy() -> None:
    ref = AttachmentRef(ref_id="blob://a1", media_type="image/png", comment_id="c1")
    assert ref.media_type == "image/png"
    assert ref.ref_id == "blob://a1"
