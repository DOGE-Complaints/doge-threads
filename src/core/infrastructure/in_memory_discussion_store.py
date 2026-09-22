from __future__ import annotations

from dataclasses import dataclass, field
from uuid import uuid4

from core.domain.comment import Comment
from core.domain.errors import CommentNotFoundError, DepthExceededError, ThreadNotFoundError
from core.domain.ports import ThreadKnobs
from core.domain.thread_key import Thread, ThreadKey


@dataclass
class CivicSideEffects:
    """Probe for AC-THR-02. Discussion store must never write these lists."""

    story_creates: list[str] = field(default_factory=list)
    story_mutations: list[str] = field(default_factory=list)
    cluster_mutations: list[str] = field(default_factory=list)


class InMemoryDiscussionStore:
    """Nested comment tree in process memory. No SQL / column lists."""

    def __init__(self, knobs: ThreadKnobs) -> None:
        self._knobs = knobs
        self._threads: dict[ThreadKey, Thread] = {}
        self._comments: dict[ThreadKey, list[Comment]] = {}
        self.civic_side_effects = CivicSideEffects()

    @property
    def knobs(self) -> ThreadKnobs:
        return self._knobs

    def attach_thread(self, key: ThreadKey) -> Thread:
        existing = self._threads.get(key)
        if existing is not None:
            return existing
        thread = Thread(key=key)
        self._threads[key] = thread
        self._comments[key] = []
        return thread

    def get_thread(self, key: ThreadKey) -> Thread | None:
        return self._threads.get(key)

    def create_comment(
        self,
        key: ThreadKey,
        body: str,
        *,
        parent_id: str | None = None,
    ) -> Comment:
        if key not in self._threads:
            raise ThreadNotFoundError(f"thread not attached: {key}")
        depth = 1
        if parent_id is not None:
            parent = self._find_comment(key, parent_id)
            if parent is None:
                raise CommentNotFoundError(f"parent comment not found: {parent_id}")
            depth = parent.depth + 1
        if depth > self._knobs.max_depth:
            raise DepthExceededError(depth, self._knobs.max_depth)
        comment = Comment(
            comment_id=uuid4().hex,
            thread_key=key,
            parent_id=parent_id,
            body=body,
            depth=depth,
        )
        self._comments[key].append(comment)
        return comment

    def list_comments(self, key: ThreadKey) -> list[Comment]:
        return list(self._comments.get(key, []))

    def _find_comment(self, key: ThreadKey, comment_id: str) -> Comment | None:
        for comment in self._comments.get(key, []):
            if comment.comment_id == comment_id:
                return comment
        return None
