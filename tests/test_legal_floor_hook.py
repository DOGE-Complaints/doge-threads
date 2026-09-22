from __future__ import annotations

import pytest

from core.domain.attachment_ref import AttachmentRef
from core.domain.errors import LegalFloorError
from core.domain.knobs import FixedThreadKnobs
from core.domain.media_floor import StubLegalMediaFloor
from core.infrastructure.in_memory_attachment_ref_store import InMemoryAttachmentRefStore


class _RecordingFloor(StubLegalMediaFloor):
    def __init__(self) -> None:
        self.seen: list[str] = []

    def honour(self, ref: AttachmentRef) -> None:
        self.seen.append(ref.ref_id)
        super().honour(ref)


def test_floor_hook_runs_before_accept() -> None:
    floor = _RecordingFloor()
    store = InMemoryAttachmentRefStore(
        knobs=FixedThreadKnobs(max_depth=4, media_allowed_types=("image/png",)),
        floor=floor,
    )
    with pytest.raises(LegalFloorError):
        store.accept_ref(
            AttachmentRef(
                ref_id="blob://blocked",
                media_type="image/png",
                comment_id="c1",
                floor_class="catastrophic",
            )
        )
    assert floor.seen == ["blob://blocked"]
    assert store.list_refs("c1") == []


def test_floor_covers_csam_and_catastrophic() -> None:
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
    with pytest.raises(LegalFloorError):
        store.accept_ref(
            AttachmentRef(
                ref_id="blob://cat",
                media_type="image/png",
                comment_id="c1",
                floor_class="catastrophic",
            )
        )
    ok = AttachmentRef(ref_id="blob://ok", media_type="image/png", comment_id="c1")
    assert store.accept_ref(ok) == ok
