"""Contract FakePostgrest for STORY-THREADS-TC-03 (unique / civic / filters)."""

from __future__ import annotations

from typing import Any

import httpx

from core.domain.knobs import FixedThreadKnobs
from core.infrastructure.db_supabase import SupabaseDatabase
from core.infrastructure.supabase_attachment_ref_store import SupabaseAttachmentRefStore
from core.infrastructure.supabase_discussion_store import SupabaseDiscussionStore
from core.infrastructure.supabase_reaction_marks_store import SupabaseReactionMarksStore

CIVIC_PATH_TOKENS = ("/stories", "/story", "/cluster", "/issues", "/doge_issues")

DDL_THREAD_COLUMNS = frozenset({"node", "entity_type", "entity_id", "created_at"})
DDL_COMMENT_COLUMNS = frozenset(
    {
        "comment_id",
        "node",
        "entity_type",
        "entity_id",
        "parent_id",
        "body",
        "depth",
        "created_at",
    }
)
DDL_MARK_COLUMNS = frozenset(
    {
        "actor_id",
        "node",
        "entity_type",
        "entity_id",
        "target_kind",
        "comment_id",
        "reaction_id",
        "created_at",
    }
)
DDL_REF_COLUMNS = frozenset({"ref_id", "comment_id", "media_type", "floor_class", "created_at"})


def http_status_error(status: int, *, method: str = "GET", path: str = "/rest/v1/x") -> httpx.HTTPStatusError:
    request = httpx.Request(method, f"http://example.test{path}")
    response = httpx.Response(status, request=request, text=f'{{"status":{status}}}')
    return httpx.HTTPStatusError(f"HTTP {status}", request=request, response=response)


class FakeContractPostgrest:
    """Four `thread_*` tables + unique marks + civic ban. Offline only."""

    def __init__(self) -> None:
        self.threads: dict[tuple[str, str, str], dict[str, Any]] = {}
        self.comments: list[dict[str, Any]] = []
        self.marks: list[dict[str, Any]] = []
        self.refs: list[dict[str, Any]] = []
        self.calls: list[tuple[str, str]] = []

    def posts(self) -> list[tuple[str, str]]:
        return [item for item in self.calls if item[0] == "POST"]

    def _eq(self, params: dict[str, str], name: str) -> str | None:
        raw = params.get(name)
        if raw is None:
            return None
        if raw == "is.null":
            return None
        return raw.removeprefix("eq.")

    def _mark_unique(self, row: dict[str, Any]) -> tuple[Any, ...]:
        base = (
            row["actor_id"],
            row["node"],
            row["entity_type"],
            row["entity_id"],
            row["target_kind"],
            row["reaction_id"],
        )
        if row.get("comment_id") is None:
            return ("root", *base)
        return ("comment", *base, row["comment_id"])

    def _request(
        self,
        *,
        method: str,
        path: str,
        params: dict[str, str] | None = None,
        json_body: Any = None,
        prefer: str | None = None,
    ) -> Any:
        del prefer
        self.calls.append((method, path))
        if any(token in path for token in CIVIC_PATH_TOKENS):
            raise AssertionError(f"civic path forbidden: {path}")
        params = params or {}
        if path == "/rest/v1/thread_threads":
            if method == "GET":
                key = (
                    self._eq(params, "node") or "",
                    self._eq(params, "entity_type") or "",
                    self._eq(params, "entity_id") or "",
                )
                row = self.threads.get(key)
                return [row] if row is not None else []
            if method == "POST":
                row = dict(json_body)
                key = (row["node"], row["entity_type"], row["entity_id"])
                self.threads[key] = row
                return [row]
        if path == "/rest/v1/thread_comments":
            if method == "GET":
                comment_id = self._eq(params, "comment_id")
                if comment_id is not None:
                    return [
                        item
                        for item in self.comments
                        if item["comment_id"] == comment_id
                        and item["node"] == self._eq(params, "node")
                        and item["entity_type"] == self._eq(params, "entity_type")
                        and item["entity_id"] == self._eq(params, "entity_id")
                    ]
                return [
                    item
                    for item in self.comments
                    if item["node"] == self._eq(params, "node")
                    and item["entity_type"] == self._eq(params, "entity_type")
                    and item["entity_id"] == self._eq(params, "entity_id")
                ]
            if method == "POST":
                row = dict(json_body)
                self.comments.append(row)
                return [row]
        if path == "/rest/v1/thread_reaction_marks":
            if method == "GET":
                return [
                    item
                    for item in self.marks
                    if item["node"] == self._eq(params, "node")
                    and item["entity_type"] == self._eq(params, "entity_type")
                    and item["entity_id"] == self._eq(params, "entity_id")
                    and item["target_kind"] == self._eq(params, "target_kind")
                    and item.get("comment_id") == self._eq(params, "comment_id")
                ]
            if method == "POST":
                row = dict(json_body)
                key = self._mark_unique(row)
                if any(self._mark_unique(item) == key for item in self.marks):
                    raise http_status_error(409, method="POST", path=path)
                self.marks.append(row)
                return [row]
        if path == "/rest/v1/thread_attachment_refs":
            if method == "GET":
                comment_id = self._eq(params, "comment_id")
                return [item for item in self.refs if item["comment_id"] == comment_id]
            if method == "POST":
                row = dict(json_body)
                self.refs.append(row)
                return [row]
        raise AssertionError(f"unexpected {method} {path}")


def make_db(fake: FakeContractPostgrest | None = None) -> tuple[SupabaseDatabase, FakeContractPostgrest]:
    fake = fake or FakeContractPostgrest()
    db = SupabaseDatabase(base_url="http://example.test", service_role_key="test-role")
    db._request = fake._request  # type: ignore[method-assign]
    return db, fake


def default_knobs() -> FixedThreadKnobs:
    return FixedThreadKnobs(max_depth=4, max_reactions_per_actor=3, media_allowed_types=("image/png",))


def discussion_store(
    fake: FakeContractPostgrest | None = None,
) -> tuple[SupabaseDiscussionStore, FakeContractPostgrest]:
    db, fake = make_db(fake)
    return SupabaseDiscussionStore(db=db, knobs=default_knobs()), fake


def marks_store(
    fake: FakeContractPostgrest | None = None,
) -> tuple[SupabaseReactionMarksStore, FakeContractPostgrest]:
    db, fake = make_db(fake)
    return SupabaseReactionMarksStore(db=db, knobs=default_knobs()), fake


def refs_store(
    fake: FakeContractPostgrest | None = None,
) -> tuple[SupabaseAttachmentRefStore, FakeContractPostgrest]:
    db, fake = make_db(fake)
    return SupabaseAttachmentRefStore(db=db, knobs=default_knobs()), fake
