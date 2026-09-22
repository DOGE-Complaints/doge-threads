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
