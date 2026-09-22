from __future__ import annotations

from core.domain.attachment_ref import FLOOR_BLOCKED_CLASSES, AttachmentRef
from core.domain.errors import LegalFloorError


class StubLegalMediaFloor:
    """In-process floor hook. Scanner vendor remains Open — no vendor API."""

    def honour(self, ref: AttachmentRef) -> None:
        """Reject CSAM / catastrophic. Not gated by node knobs."""
        if ref.floor_class in FLOOR_BLOCKED_CLASSES:
            raise LegalFloorError(f"legal media floor blocked: {ref.floor_class}")
