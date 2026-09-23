"""t05 — STORY-THREADS-TC-01 story gate: U-* TRACEABILITY, *Error coverage, AC-THR-01."""

from __future__ import annotations

from asgi_public_paths import CURRENT_PUBLIC_GET_PATHS

import inspect
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from core.api.asgi_app import app
from core.application.map_shell_knobs import map_pack_shell_settings_to_knobs
from core.application.write_gate import IdentityVerifiedWriteGate, create_comment_if_allowed
from core.domain import errors as domain_errors
from core.domain.attachment_ref import AttachmentRef
from core.domain.errors import (
    AttachmentRefError,
    CommentNotFoundError,
    DepthExceededError,
    DiscussionStoreError,
    LegalFloorError,
    MaxReactionsExceededError,
    MediaTypeNotAllowedError,
    ReactionDisabledError,
    ReactionLayerError,
    ReactionMarkError,
    ReactionMutexError,
    StoryNarrativeError,
    ThreadContextError,
    ThreadNotFoundError,
    UnknownReactionIdError,
    WriteDeniedError,
)
from core.domain.knobs import FixedThreadKnobs
from core.domain.reaction_mark import ReactionMark, ReactionTarget
from core.domain.story_narrative import assert_no_story_narrative
from core.domain.thread_key import ThreadKey
from core.infrastructure.in_memory_attachment_ref_store import InMemoryAttachmentRefStore
from core.infrastructure.in_memory_discussion_store import InMemoryDiscussionStore
from core.infrastructure.in_memory_reaction_marks_store import InMemoryReactionMarksStore
from tc01_traceability import TC01_ERROR_CLASSES, TC01_SCENARIO_IDS

_TESTS = Path(__file__).resolve().parent
_SRC_ROOT = _TESTS.parent / "src"
_TC01_FILES = (
    _TESTS / "tc01_traceability.py",
    _TESTS / "test_tc01_threadkey_discussion_edges.py",
    _TESTS / "test_tc01_marks_catalog_edges.py",
    _TESTS / "test_tc01_attachment_floor_edges.py",
    _TESTS / "test_tc01_gate_compose_edges.py",
    _TESTS / "test_story_gate_tc_01.py",
)


def _asgi_paths() -> list[str]:
    return sorted(
        path
        for path in (
            getattr(route, "path", None) for route in app.routes if getattr(route, "methods", None)
        )
        if isinstance(path, str)
    )


def _key() -> ThreadKey:
    return ThreadKey(node="n1", entity_type="Issue", entity_id="e1")


def _trigger_discussion_missing() -> None:
    InMemoryDiscussionStore(knobs=FixedThreadKnobs(max_depth=2)).create_comment(_key(), "x")


def _trigger_bad_parent() -> None:
    store = InMemoryDiscussionStore(knobs=FixedThreadKnobs(max_depth=2))
    store.attach_thread(_key())
    store.create_comment(_key(), "x", parent_id="missing")


def _trigger_depth() -> None:
    store = InMemoryDiscussionStore(knobs=FixedThreadKnobs(max_depth=1))
    store.attach_thread(_key())
    root = store.create_comment(_key(), "d1")
    store.create_comment(_key(), "d2", parent_id=root.comment_id)


def _trigger_write_denied() -> None:
    mock = MagicMock()
    mock.fetch_me.return_value = {"data": {"identity_verified": False}}
    store = InMemoryDiscussionStore(knobs=FixedThreadKnobs(max_depth=2))
    create_comment_if_allowed(store, IdentityVerifiedWriteGate(mock), "tok", _key(), "nope")


def _trigger_unknown_reaction() -> None:
    InMemoryReactionMarksStore(knobs=FixedThreadKnobs(max_depth=2)).add_mark(
        ReactionMark(
            actor_id="a1",
            target=ReactionTarget(kind="thread_root", thread_key=_key()),
            reaction_id="not_in_v1",
        )
    )


def _trigger_disabled() -> None:
    store = InMemoryReactionMarksStore(
        knobs=FixedThreadKnobs(
            max_depth=2,
            max_reactions_per_actor=2,
            reactions_enable={"acknowledge": False},
        )
    )
    store.add_mark(
        ReactionMark(
            actor_id="a1",
            target=ReactionTarget(kind="thread_root", thread_key=_key()),
            reaction_id="acknowledge",
        )
    )


def _trigger_mutex() -> None:
    store = InMemoryReactionMarksStore(
        knobs=FixedThreadKnobs(max_depth=2, max_reactions_per_actor=3)
    )
    target = ReactionTarget(kind="comment", thread_key=_key(), comment_id="c1")
    store.add_mark(ReactionMark(actor_id="a1", target=target, reaction_id="agree"))
    store.add_mark(ReactionMark(actor_id="a1", target=target, reaction_id="disagree"))


def _trigger_layer() -> None:
    InMemoryReactionMarksStore(knobs=FixedThreadKnobs(max_depth=2)).add_mark(
        ReactionMark(
            actor_id="a1",
            target=ReactionTarget(kind="thread_root", thread_key=_key()),
            reaction_id="off_topic",
        )
    )


def _trigger_max_marks() -> None:
    store = InMemoryReactionMarksStore(
        knobs=FixedThreadKnobs(max_depth=2, max_reactions_per_actor=1)
    )
    target = ReactionTarget(kind="thread_root", thread_key=_key())
    store.add_mark(ReactionMark(actor_id="a1", target=target, reaction_id="acknowledge"))
    store.add_mark(ReactionMark(actor_id="a1", target=target, reaction_id="support"))


def _trigger_media() -> None:
    InMemoryAttachmentRefStore(
        knobs=FixedThreadKnobs(max_depth=2, media_allowed_types=("image/png",))
    ).accept_ref(AttachmentRef(ref_id="blob://vid", media_type="video/mp4", comment_id="c1"))


def _trigger_floor() -> None:
    InMemoryAttachmentRefStore(knobs=FixedThreadKnobs(max_depth=2)).accept_ref(
        AttachmentRef(
            ref_id="blob://csam",
            media_type="image/png",
            comment_id="c1",
            floor_class="csam",
        )
    )


_ERROR_TRIGGERS: dict[type[Exception], object] = {
    DiscussionStoreError: _trigger_discussion_missing,
    ThreadNotFoundError: _trigger_discussion_missing,
    CommentNotFoundError: _trigger_bad_parent,
    DepthExceededError: _trigger_depth,
    ThreadContextError: lambda: map_pack_shell_settings_to_knobs({}),
    StoryNarrativeError: lambda: assert_no_story_narrative({"story": "x"}),
    WriteDeniedError: _trigger_write_denied,
    ReactionMarkError: _trigger_unknown_reaction,
    UnknownReactionIdError: _trigger_unknown_reaction,
    ReactionDisabledError: _trigger_disabled,
    ReactionMutexError: _trigger_mutex,
    ReactionLayerError: _trigger_layer,
    MaxReactionsExceededError: _trigger_max_marks,
    AttachmentRefError: _trigger_floor,
    MediaTypeNotAllowedError: _trigger_media,
    LegalFloorError: _trigger_floor,
}


def test_errors_py_class_count_matches_ssot() -> None:
    live = {
        name
        for name, obj in vars(domain_errors).items()
        if isinstance(obj, type) and name.endswith("Error") and issubclass(obj, Exception)
    }
    assert live == TC01_ERROR_CLASSES
    assert len(live) == 16


@pytest.mark.parametrize("exc_name", sorted(TC01_ERROR_CLASSES))
def test_every_domain_error_has_failing_path(exc_name: str) -> None:
    exc_type = getattr(domain_errors, exc_name)
    trigger = _ERROR_TRIGGERS[exc_type]
    with pytest.raises(exc_type):
        trigger()


def test_all_u_scenario_ids_present_for_traceability() -> None:
    corpus = "\n".join(path.read_text(encoding="utf-8") for path in _TC01_FILES)
    missing = sorted(item for item in TC01_SCENARIO_IDS if item not in corpus)
    assert missing == []
    families = {item.split("-", 2)[1] for item in TC01_SCENARIO_IDS}
    assert families == {"KEY", "DISC", "MARK", "ATT", "GATE", "CMP"}


def test_ac_thr_01_no_new_public_routes() -> None:
    assert _asgi_paths() == CURRENT_PUBLIC_GET_PATHS
    asgi = (_SRC_ROOT / "core" / "api" / "asgi_app.py").read_text(encoding="utf-8")
    for name in ("/comment", "/reaction", "/attachment"):
        assert f'@app.get("{name}' not in asgi
        assert f'@app.post("{name}' not in asgi


def test_error_triggers_cover_every_errors_py_class() -> None:
    named = {cls.__name__ for cls in _ERROR_TRIGGERS}
    assert named == TC01_ERROR_CLASSES
    for cls in _ERROR_TRIGGERS:
        assert inspect.isclass(cls)
