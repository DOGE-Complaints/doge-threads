"""t01 + t02 — stub fixture + O-WR write kinds × verified × backends."""

from __future__ import annotations

import pytest

from core.domain.attachment_ref import AttachmentRef
from core.domain.errors import WriteDeniedError
from core.domain.reaction_mark import ReactionMark, ReactionTarget
from core.domain.thread_key import ThreadKey
from core.infrastructure.in_memory_attachment_ref_store import InMemoryAttachmentRefStore
from core.infrastructure.in_memory_discussion_store import InMemoryDiscussionStore
from core.infrastructure.in_memory_reaction_marks_store import InMemoryReactionMarksStore
from core.infrastructure.supabase_attachment_ref_store import SupabaseAttachmentRefStore
from core.infrastructure.supabase_discussion_store import SupabaseDiscussionStore
from core.infrastructure.supabase_reaction_marks_store import SupabaseReactionMarksStore
from tc02_orch_fixtures import make_orch_harness, patch_gateway
from threadcontext_fixtures import SAMPLE_ISSUE_ID


def _key() -> ThreadKey:
    return ThreadKey(node="n1", entity_type="Issue", entity_id="e1")


def _mark() -> ReactionMark:
    return ReactionMark(
        actor_id="a1",
        target=ReactionTarget(kind="thread_root", thread_key=_key()),
        reaction_id="acknowledge",
    )


def _ref() -> AttachmentRef:
    return AttachmentRef(ref_id="blob://ok", media_type="image/png", comment_id="c1")


def test_t01_fixture_wires_supabase_stub_orch() -> None:
    harness = make_orch_harness(backend="supabase_stub", verified=True)
    assert isinstance(harness.discussion, SupabaseDiscussionStore)
    assert isinstance(harness.reactions, SupabaseReactionMarksStore)
    assert isinstance(harness.attachments, SupabaseAttachmentRefStore)
    assert harness.fake is not None
    assert harness.fake.calls == []


def test_t01_fixture_keeps_in_memory_orch() -> None:
    harness = make_orch_harness(backend="in_memory", verified=True)
    assert isinstance(harness.discussion, InMemoryDiscussionStore)
    assert isinstance(harness.reactions, InMemoryReactionMarksStore)
    assert isinstance(harness.attachments, InMemoryAttachmentRefStore)
    assert harness.fake is None


@pytest.mark.parametrize("backend", ("in_memory", "supabase_stub"))
@pytest.mark.parametrize("verified", (True, False))
@pytest.mark.parametrize("kind", ("comment", "reaction", "attachment"))
def test_o_wr_write_kinds_verified_matrix(
    backend: str, verified: bool, kind: str
) -> None:
    scenario_id = f"O-WR-{kind}-{'true' if verified else 'false'}-{backend}"
    harness = make_orch_harness(backend=backend, verified=verified)  # type: ignore[arg-type]
    key = _key()
    with patch_gateway(harness.mock_http):
        if verified:
            if kind == "comment":
                comment = harness.orchestrator.write_comment(
                    "tok", SAMPLE_ISSUE_ID, key, "hello"
                )
                assert comment.body == "hello"
                assert harness.discussion.list_comments(key) == [comment]
            elif kind == "reaction":
                mark = _mark()
                stored = harness.orchestrator.write_reaction("tok", SAMPLE_ISSUE_ID, mark)
                assert stored.reaction_id == "acknowledge"
                assert harness.reactions.list_marks(mark.target) == [stored]
            else:
                ref = _ref()
                stored_ref = harness.orchestrator.write_attachment_ref(
                    "tok", SAMPLE_ISSUE_ID, ref
                )
                assert stored_ref.ref_id == "blob://ok"
                assert harness.attachments.list_refs("c1") == [stored_ref]
            harness.me.fetch_me.assert_called_with("tok")
        else:
            with pytest.raises(WriteDeniedError):
                if kind == "comment":
                    harness.orchestrator.write_comment("tok", SAMPLE_ISSUE_ID, key, "nope")
                elif kind == "reaction":
                    harness.orchestrator.write_reaction("tok", SAMPLE_ISSUE_ID, _mark())
                else:
                    harness.orchestrator.write_attachment_ref("tok", SAMPLE_ISSUE_ID, _ref())
            if kind == "comment":
                assert harness.discussion.list_comments(key) == []
            elif kind == "reaction":
                assert harness.reactions.list_marks(_mark().target) == []
            else:
                assert harness.attachments.list_refs("c1") == []
            if harness.fake is not None:
                assert harness.fake.posts() == []
    assert scenario_id.startswith("O-WR-")
