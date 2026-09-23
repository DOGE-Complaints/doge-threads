from __future__ import annotations

from typing import Any

from core.api.dependencies import ApiDependencies
from core.api.envelope import build_success_envelope, ensure_trace_id
from core.api.thread_key_builder import build_issue_thread_key
from core.config import ConfigError
from core.domain.comment import Comment
from core.domain.ports import ThreadKnobs


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
