from __future__ import annotations


class DiscussionStoreError(Exception):
    """Base error for discussion-store operations."""


class ThreadNotFoundError(DiscussionStoreError):
    """Raised when a comment targets a thread that was not attached."""


class CommentNotFoundError(DiscussionStoreError):
    """Raised when a parent comment id is missing from the thread."""


class DepthExceededError(DiscussionStoreError):
    """Raised when comment depth is greater than injected knobs.max_depth."""

    def __init__(self, depth: int, max_depth: int) -> None:
        self.depth = depth
        self.max_depth = max_depth
        super().__init__(f"comment depth {depth} exceeds knobs.max_depth {max_depth}")


class ThreadContextError(Exception):
    """ThreadContext pull or compose failure."""


class StoryNarrativeError(ThreadContextError):
    """Raised when Story narrative keys appear in settings or composed context."""


class WriteDeniedError(Exception):
    """Raised when a thread write is denied by the verified-boolean gate."""


class ReactionMarkError(Exception):
    """Base error for reaction mark store operations."""


class UnknownReactionIdError(ReactionMarkError):
    """Raised when reaction_id is not a reactions.v1 catalog id."""


class ReactionDisabledError(ReactionMarkError):
    """Raised when knobs disable this reaction_id."""


class ReactionMutexError(ReactionMarkError):
    """Raised when agree and disagree would both apply on the same target."""


class ReactionLayerError(ReactionMarkError):
    """Raised when a mark violates catalog layer / target rules."""


class MaxReactionsExceededError(ReactionMarkError):
    """Raised when actor marks on a target exceed knobs.max_reactions_per_actor."""


class AttachmentRefError(Exception):
    """Base error for attachment reference store operations."""


class MediaTypeNotAllowedError(AttachmentRefError):
    """Raised when media_type is outside knobs.media_allowed_types."""


class LegalFloorError(AttachmentRefError):
    """Raised when the platform legal media floor blocks CSAM / catastrophic."""
