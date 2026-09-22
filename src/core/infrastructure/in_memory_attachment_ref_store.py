from __future__ import annotations

from core.domain.attachment_ref import AttachmentRef
from core.domain.errors import MediaTypeNotAllowedError
from core.domain.media_floor import StubLegalMediaFloor
from core.domain.ports import MediaFloor, ThreadKnobs


class InMemoryAttachmentRefStore:
    """In-process attachment refs. No bytes / SQL / column lists / public path."""

    def __init__(self, knobs: ThreadKnobs, floor: MediaFloor | None = None) -> None:
        self._knobs = knobs
        self._floor = floor or StubLegalMediaFloor()
        self._refs: list[AttachmentRef] = []

    @property
    def knobs(self) -> ThreadKnobs:
        return self._knobs

    @property
    def floor(self) -> MediaFloor:
        return self._floor

    def accept_ref(self, ref: AttachmentRef) -> AttachmentRef:
        self._floor.honour(ref)
        allowed = self._knobs.media_allowed_types
        if allowed and ref.media_type not in allowed:
            raise MediaTypeNotAllowedError(
                f"media_type {ref.media_type!r} not in knobs.media_allowed_types"
            )
        self._refs.append(ref)
        return ref

    def list_refs(self, comment_id: str) -> list[AttachmentRef]:
        return [item for item in self._refs if item.comment_id == comment_id]
