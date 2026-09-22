"""t01 — C-PG-GET-* empty GET, eq filters, comment_id, is.null root marks."""

from __future__ import annotations

from core.domain.attachment_ref import AttachmentRef
from core.domain.reaction_mark import ReactionMark, ReactionTarget
from core.domain.thread_key import ThreadKey
from tc03_fake_postgrest import discussion_store, marks_store, refs_store
from tc03_traceability import TC03_SCENARIO_IDS

_KEY = ThreadKey(node="n1", entity_type="Issue", entity_id="e1")
_OTHER = ThreadKey(node="n2", entity_type="Issue", entity_id="e9")


def _root() -> ReactionTarget:
    return ReactionTarget(kind="thread_root", thread_key=_KEY)


def _comment_target(comment_id: str) -> ReactionTarget:
    return ReactionTarget(kind="comment", thread_key=_KEY, comment_id=comment_id)


def test_c_pg_get_empty_thread_comments_marks_refs() -> None:
    assert "C-PG-GET-empty-thread" in TC03_SCENARIO_IDS
    store, _fake = discussion_store()
    assert store.get_thread(_KEY) is None  # C-PG-GET-empty-thread
    assert store.list_comments(_KEY) == []  # C-PG-GET-empty-comments
    marks, _mfake = marks_store()
    assert marks.list_marks(_root()) == []  # C-PG-GET-empty-marks
    refs, _rfake = refs_store()
    assert refs.list_refs("c-missing") == []  # C-PG-GET-empty-refs


def test_c_pg_get_eq_node_type_id() -> None:
    assert "C-PG-GET-eq-node-type-id" in TC03_SCENARIO_IDS
    store, _fake = discussion_store()
    attached = store.attach_thread(_KEY)
    assert store.get_thread(_KEY) == attached
    assert store.get_thread(_OTHER) is None
    store.create_comment(_KEY, "only-here")
    assert [item.body for item in store.list_comments(_KEY)] == ["only-here"]
    assert store.list_comments(_OTHER) == []


def test_c_pg_get_eq_comment_id_and_is_null_root_marks() -> None:
    assert "C-PG-GET-eq-comment-id" in TC03_SCENARIO_IDS
    assert "C-PG-GET-is-null-root-marks" in TC03_SCENARIO_IDS
    disc, fake = discussion_store()
    disc.attach_thread(_KEY)
    root = disc.create_comment(_KEY, "root")
    child = disc.create_comment(_KEY, "child", parent_id=root.comment_id)
    assert disc._find_comment(_KEY, root.comment_id) is not None
    assert disc._find_comment(_KEY, "missing") is None
    assert child.parent_id == root.comment_id

    marks, mfake = marks_store(fake)
    marks.add_mark(ReactionMark(actor_id="a1", target=_root(), reaction_id="acknowledge"))
    marks.add_mark(
        ReactionMark(actor_id="a1", target=_comment_target(root.comment_id), reaction_id="agree")
    )
    root_marks = marks.list_marks(_root())
    assert [item.reaction_id for item in root_marks] == ["acknowledge"]
    comment_marks = marks.list_marks(_comment_target(root.comment_id))
    assert [item.reaction_id for item in comment_marks] == ["agree"]
    assert marks.list_marks(_comment_target("other")) == []

    refs, _rfake = refs_store(fake)
    refs.accept_ref(AttachmentRef(ref_id="blob://ok", media_type="image/png", comment_id=root.comment_id))
    assert [item.ref_id for item in refs.list_refs(root.comment_id)] == ["blob://ok"]
    assert refs.list_refs("nope") == []
    assert mfake._eq({"comment_id": "is.null"}, "comment_id") is None
