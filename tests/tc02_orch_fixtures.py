"""t01 — orchestrator + FakePostgrest (all four thread_* tables) + stub Me/Gateway."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal
from unittest.mock import MagicMock

from core.application.write_gate import IdentityVerifiedWriteGate
from core.application.write_orchestrator import ThreadWriteOrchestrator
from core.domain.knobs import FixedThreadKnobs
from core.infrastructure.db_supabase import SupabaseDatabase
from core.infrastructure.in_memory_attachment_ref_store import InMemoryAttachmentRefStore
from core.infrastructure.in_memory_discussion_store import InMemoryDiscussionStore
from core.infrastructure.in_memory_reaction_marks_store import InMemoryReactionMarksStore
from core.infrastructure.supabase_attachment_ref_store import SupabaseAttachmentRefStore
from core.infrastructure.supabase_discussion_store import SupabaseDiscussionStore
from core.infrastructure.supabase_reaction_marks_store import SupabaseReactionMarksStore
from threadcontext_fixtures import stub_gateway_client
from write_orchestrator_fixtures import patch_gateway

Backend = Literal["in_memory", "supabase_stub"]

_CIVIC_PATH_TOKENS = ("/stories", "/story", "/cluster", "/issues", "/doge_issues")


class FakeOrchPostgrest:
    """Offline PostgREST stub for discussion + marks + refs. No network."""

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
        if any(token in path for token in _CIVIC_PATH_TOKENS):
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


@dataclass
class OrchHarness:
    backend: Backend
    orchestrator: ThreadWriteOrchestrator
    discussion: Any
    reactions: Any
    attachments: Any
    mock_http: MagicMock
    me: MagicMock
    fake: FakeOrchPostgrest | None = None
    order: list[str] = field(default_factory=list)


def default_knobs() -> FixedThreadKnobs:
    return FixedThreadKnobs(
        max_depth=3,
        max_reactions_per_actor=3,
        media_allowed_types=("image/png",),
    )


def make_orch_harness(
    *,
    backend: Backend,
    verified: bool = True,
    knobs: FixedThreadKnobs | None = None,
) -> OrchHarness:
    knobs = knobs or default_knobs()
    order: list[str] = []
    me = MagicMock()

    def _fetch_me(token: str) -> dict[str, Any]:
        order.append("me")
        return {"data": {"identity_verified": verified}}

    me.fetch_me.side_effect = _fetch_me
    gateway, mock_http = stub_gateway_client()
    real_request = mock_http.request.side_effect

    def _gw_request(*args: Any, **kwargs: Any) -> Any:
        order.append("gw")
        return real_request(*args, **kwargs)

    mock_http.request.side_effect = _gw_request
    fake: FakeOrchPostgrest | None = None
    if backend == "in_memory":
        discussion: Any = InMemoryDiscussionStore(knobs=knobs)
        reactions: Any = InMemoryReactionMarksStore(knobs=knobs)
        attachments: Any = InMemoryAttachmentRefStore(knobs=knobs)
    else:
        fake = FakeOrchPostgrest()
        db = SupabaseDatabase(base_url="http://example.test", service_role_key="test-role")

        def _db_request(**kwargs: Any) -> Any:
            assert fake is not None
            if kwargs.get("method") == "POST":
                order.append("db")
            return fake._request(**kwargs)

        db._request = _db_request  # type: ignore[method-assign]
        discussion = SupabaseDiscussionStore(db=db, knobs=knobs)
        reactions = SupabaseReactionMarksStore(db=db, knobs=knobs)
        attachments = SupabaseAttachmentRefStore(db=db, knobs=knobs)
    orchestrator = ThreadWriteOrchestrator(
        gateway=gateway,
        write_gate=IdentityVerifiedWriteGate(me),
        discussion_store=discussion,
        reaction_store=reactions,
        attachment_store=attachments,
    )
    return OrchHarness(
        backend=backend,
        orchestrator=orchestrator,
        discussion=discussion,
        reactions=reactions,
        attachments=attachments,
        mock_http=mock_http,
        me=me,
        fake=fake,
        order=order,
    )


__all__ = [
    "Backend",
    "FakeOrchPostgrest",
    "OrchHarness",
    "default_knobs",
    "make_orch_harness",
    "patch_gateway",
]
