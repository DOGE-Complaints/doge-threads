from __future__ import annotations

from collections import Counter
from typing import Any, Literal

from pydantic import BaseModel

from core.api.dependencies import ApiDependencies
from core.api.envelope import build_error_envelope, build_success_envelope, ensure_trace_id
from core.api.thread_key_builder import build_issue_thread_key
from core.config import ConfigError
from core.domain.attachment_ref import FLOOR_OK, AttachmentRef
from core.domain.comment import Comment
from core.domain.errors import AttachmentRefError
from core.domain.ports import ThreadKnobs
from core.domain.reaction_mark import ReactionMark, ReactionTarget
from core.identity.me_client import IdentityMeError, parse_me_actor_id


class CommentWriteBody(BaseModel):
    """FE §3 comment create/reply body."""

    body: str
    parent_id: str | None = None


class ReactionWriteBody(BaseModel):
    """FE §5 reaction add/remove body."""

    target_kind: Literal["thread_root", "comment"]
    comment_id: str | None = None
    reaction_id: str
    op: Literal["add", "remove"]


class AttachmentWriteBody(BaseModel):
    """FE §6 attachment-ref body. Optional floor_class is domain metadata (default ok)."""

    ref_id: str
    media_type: str
    comment_id: str
    floor_class: str = FLOOR_OK


def knobs_snapshot(knobs: ThreadKnobs) -> dict[str, Any]:
    """Arch minimum knobs JSON (02-routes-and-contracts)."""
    return {
        "max_depth": knobs.max_depth,
        "max_reactions_per_actor": knobs.max_reactions_per_actor,
        "reactions_enable": dict(knobs.reactions_enable),
        "media_allowed_types": list(knobs.media_allowed_types),
    }


def _comment_payload(comment: Comment) -> dict[str, Any]:
    return {
        "comment_id": comment.comment_id,
        "parent_id": comment.parent_id,
        "depth": comment.depth,
        "body": comment.body,
    }


def handle_knobs(
    dependencies: ApiDependencies, trace_id: str | None = None
) -> dict[str, Any]:
    """Node-level FixedThreadKnobs snapshot. No issue_id; no compose pull."""
    knobs = dependencies.thread_knobs
    if knobs is None:
        raise ConfigError("thread_knobs is not wired")
    return build_success_envelope(
        data=knobs_snapshot(knobs),
        trace_id=ensure_trace_id(trace_id),
    ).as_dict()


def handle_tree(
    dependencies: ApiDependencies,
    issue_id: str,
    trace_id: str | None = None,
) -> dict[str, Any]:
    """Public tree read: issue_id + comments[] only (T1; no knobs)."""
    store = dependencies.discussion_store
    if store is None:
        raise ConfigError("discussion_store is not wired")
    key = build_issue_thread_key(
        issue_id=issue_id,
        schema_id=dependencies.config.dogestonia_schema_id,
    )
    comments = store.list_comments(key)
    return build_success_envelope(
        data={
            "issue_id": issue_id,
            "comments": [_comment_payload(comment) for comment in comments],
        },
        trace_id=ensure_trace_id(trace_id),
    ).as_dict()


def handle_create_comment(
    dependencies: ApiDependencies,
    issue_id: str,
    payload: CommentWriteBody,
    bearer_token: str,
    trace_id: str | None = None,
) -> dict[str, Any]:
    """Thin wrap of orchestrator write_comment. ThreadKey from HTTP-02 builder."""
    orchestrator = dependencies.write_orchestrator
    if orchestrator is None:
        raise ConfigError("write_orchestrator is not wired")
    key = build_issue_thread_key(
        issue_id=issue_id,
        schema_id=dependencies.config.dogestonia_schema_id,
    )
    comment = orchestrator.write_comment(
        bearer_token,
        issue_id,
        key,
        payload.body,
        parent_id=payload.parent_id,
    )
    return build_success_envelope(
        data=_comment_payload(comment),
        trace_id=ensure_trace_id(trace_id),
    ).as_dict()


def _actor_id(dependencies: ApiDependencies, bearer_token: str) -> str:
    client = dependencies.identity_me
    if client is None:
        raise ConfigError("identity_me is not wired")
    body = client.fetch_me(bearer_token)
    if body is None:
        raise IdentityMeError("Identity /me returned no body.")
    return parse_me_actor_id(body)


def _reaction_success_data(
    *,
    issue_id: str,
    payload: ReactionWriteBody,
    actor_id: str,
    marks: list[ReactionMark],
) -> dict[str, Any]:
    counts = Counter(item.reaction_id for item in marks)
    summary = [
        {"reaction_id": reaction_id, "count": count}
        for reaction_id, count in sorted(counts.items())
    ]
    selected = sorted(
        item.reaction_id for item in marks if item.actor_id == actor_id
    )
    return {
        "issue_id": issue_id,
        "target_kind": payload.target_kind,
        "comment_id": payload.comment_id,
        "reaction_id": payload.reaction_id,
        "op": payload.op,
        "selected": selected,
        "summary_marks": summary,
        "aggregate_count": len(marks),
    }


def handle_reaction(
    dependencies: ApiDependencies,
    issue_id: str,
    payload: ReactionWriteBody,
    bearer_token: str,
    trace_id: str | None = None,
) -> dict[str, Any]:
    """Thin wrap write_reaction / remove_reaction. ThreadKey from HTTP-02 builder."""
    orchestrator = dependencies.write_orchestrator
    if orchestrator is None:
        raise ConfigError("write_orchestrator is not wired")
    key = build_issue_thread_key(
        issue_id=issue_id,
        schema_id=dependencies.config.dogestonia_schema_id,
    )
    target = ReactionTarget(
        kind=payload.target_kind,
        thread_key=key,
        comment_id=payload.comment_id,
    )
    actor_id = _actor_id(dependencies, bearer_token)
    mark = ReactionMark(
        actor_id=actor_id,
        target=target,
        reaction_id=payload.reaction_id,
    )
    if payload.op == "add":
        orchestrator.write_reaction(bearer_token, issue_id, mark)
    else:
        orchestrator.remove_reaction(bearer_token, issue_id, mark)
    marks = orchestrator.list_reaction_marks(target)
    return build_success_envelope(
        data=_reaction_success_data(
            issue_id=issue_id,
            payload=payload,
            actor_id=actor_id,
            marks=marks,
        ),
        trace_id=ensure_trace_id(trace_id),
    ).as_dict()


def handle_create_attachment_ref(
    dependencies: ApiDependencies,
    issue_id: str,
    payload: AttachmentWriteBody,
    bearer_token: str,
    trace_id: str | None = None,
) -> dict[str, Any]:
    """Thin wrap write_attachment_ref. Floor/allowlist → attach-denied envelope."""
    orchestrator = dependencies.write_orchestrator
    if orchestrator is None:
        raise ConfigError("write_orchestrator is not wired")
    ref = AttachmentRef(
        ref_id=payload.ref_id,
        media_type=payload.media_type,
        comment_id=payload.comment_id,
        floor_class=payload.floor_class,
    )
    try:
        stored = orchestrator.write_attachment_ref(bearer_token, issue_id, ref)
    except AttachmentRefError as exc:
        return build_error_envelope(
            exc,
            trace_id=ensure_trace_id(trace_id),
            details={"reason": "attach-denied"},
        ).as_dict()
    return build_success_envelope(
        data={
            "ref_id": stored.ref_id,
            "media_type": stored.media_type,
            "comment_id": stored.comment_id,
            "floor_class": stored.floor_class,
        },
        trace_id=ensure_trace_id(trace_id),
    ).as_dict()
