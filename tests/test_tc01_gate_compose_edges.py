"""t04 — U-GATE write-gate parse + U-CMP compose/narrative (offline, no network)."""

from __future__ import annotations

from copy import deepcopy
from unittest.mock import MagicMock

import pytest

from core.application.compose_thread_context import ThreadContextComposer
from core.application.map_shell_knobs import map_pack_shell_settings_to_knobs
from core.application.write_gate import (
    IdentityVerifiedWriteGate,
    attach_thread_if_allowed,
    create_comment_if_allowed,
)
from core.domain.errors import StoryNarrativeError, ThreadContextError, WriteDeniedError
from core.domain.knobs import FixedThreadKnobs
from core.domain.story_narrative import FORBIDDEN_STORY_KEYS
from core.domain.thread_context import IssueProjection
from core.domain.thread_key import ThreadKey
from core.identity.me_client import IdentityMeError, parse_me_identity_verified
from core.infrastructure.in_memory_discussion_store import InMemoryDiscussionStore
from threadcontext_fixtures import SAMPLE_SETTINGS_PAYLOAD, SAMPLE_STORY_ID

_FORBIDDEN_IDS = {
    "story": "U-CMP-forbidden-story",
    "stories": "U-CMP-forbidden-stories",
    "story_body": "U-CMP-forbidden-story_body",
    "narrative": "U-CMP-forbidden-narrative",
    "original_text": "U-CMP-forbidden-original_text",
    "thread_context": "U-CMP-forbidden-thread_context",
    "ThreadContext": "U-CMP-forbidden-ThreadContext",
}


def _store() -> InMemoryDiscussionStore:
    return InMemoryDiscussionStore(knobs=FixedThreadKnobs(max_depth=3))


def _key() -> ThreadKey:
    return ThreadKey(node="n1", entity_type="Issue", entity_id="e1")


def _deny_gate(*, body: dict | None = None, error: Exception | None = None) -> IdentityVerifiedWriteGate:
    mock = MagicMock()
    if error is not None:
        mock.fetch_me.side_effect = error
    else:
        mock.fetch_me.return_value = body
    return IdentityVerifiedWriteGate(mock)


@pytest.mark.parametrize(
    ("body", "scenario_id"),
    [
        ({"data": {"supabase_user_id": "u1"}}, "U-GATE-missing-identity-verified"),
        ({"data": {"identity_verified": False}}, "U-GATE-false"),
        ({"data": {"identity_verified": "yes"}}, "U-GATE-non-bool"),
        ({"data": {"phone_verified": True}}, "U-GATE-phone-only"),
    ],
)
def test_u_gate_identity_verified_deny(body: dict, scenario_id: str) -> None:
    store = _store()
    key = _key()
    if scenario_id == "U-GATE-missing-identity-verified":
        assert parse_me_identity_verified(body) is None
    elif scenario_id == "U-GATE-false":
        assert parse_me_identity_verified(body) is False
    elif scenario_id == "U-GATE-non-bool":
        with pytest.raises(IdentityMeError):
            parse_me_identity_verified(body)
    with pytest.raises(WriteDeniedError):
        create_comment_if_allowed(store, _deny_gate(body=body), "tok", key, "nope")
    assert store.list_comments(key) == []
    assert scenario_id.startswith("U-GATE-")


@pytest.mark.parametrize(
    ("error", "scenario_id"),
    [
        (IdentityMeError("Identity /me timed out."), "U-GATE-timeout"),
        (IdentityMeError("Identity /me returned 503."), "U-GATE-5xx"),
    ],
)
def test_u_gate_transport_deny(error: IdentityMeError, scenario_id: str) -> None:
    store = _store()
    key = _key()
    with pytest.raises(WriteDeniedError):
        create_comment_if_allowed(store, _deny_gate(error=error), "tok", key, "nope")
    assert store.list_comments(key) == []
    assert scenario_id.startswith("U-GATE-")


def test_u_gate_true_allow() -> None:
    """U-GATE-true-allow"""
    store = _store()
    key = _key()
    mock = MagicMock()
    mock.fetch_me.return_value = {"data": {"identity_verified": True}}
    gate = IdentityVerifiedWriteGate(mock)
    assert parse_me_identity_verified({"data": {"identity_verified": True}}) is True
    attach_thread_if_allowed(store, gate, "tok", key)
    comment = create_comment_if_allowed(store, gate, "tok", key, "ok")
    assert comment.body == "ok"
    assert store.get_thread(key) is not None


@pytest.mark.parametrize("forbidden_key", sorted(FORBIDDEN_STORY_KEYS))
def test_u_cmp_every_forbidden_story_key(forbidden_key: str) -> None:
    scenario_id = _FORBIDDEN_IDS[forbidden_key]
    tainted = deepcopy(SAMPLE_SETTINGS_PAYLOAD)
    tainted["pack_shell_settings"][forbidden_key] = "must-reject"
    with pytest.raises(StoryNarrativeError) as exc:
        ThreadContextComposer().compose(
            IssueProjection(issue_id="iss-1", opaque_story_ids=(SAMPLE_STORY_ID,)),
            tainted,
        )
    assert isinstance(exc.value, ThreadContextError)
    assert scenario_id == f"U-CMP-forbidden-{forbidden_key}"


def test_u_cmp_opaque_story_ids_ok() -> None:
    """U-CMP-opaque-story-ids-ok"""
    context = ThreadContextComposer().compose(
        IssueProjection(issue_id="iss-1", opaque_story_ids=(SAMPLE_STORY_ID,)),
        SAMPLE_SETTINGS_PAYLOAD,
    )
    mapping = context.as_mapping()
    assert mapping["opaque_story_ids"] == [SAMPLE_STORY_ID]
    assert "story_body" not in mapping
    for key in FORBIDDEN_STORY_KEYS:
        assert key not in mapping


def test_u_cmp_missing_knobs_fields_fail_closed() -> None:
    """U-CMP-missing-knobs-fields"""
    with pytest.raises(ThreadContextError, match="pack_shell_settings missing"):
        map_pack_shell_settings_to_knobs({})
    with pytest.raises(ThreadContextError, match="threads missing"):
        map_pack_shell_settings_to_knobs({"pack_shell_settings": {}})
    knobs = map_pack_shell_settings_to_knobs({"pack_shell_settings": {"threads": {}}})
    assert knobs.max_depth == 1
    assert knobs.max_reactions_per_actor == 1
    assert knobs.reactions_enable == {}
    assert knobs.media_allowed_types == ()
