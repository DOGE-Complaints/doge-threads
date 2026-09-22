"""t03 + t04 — O-DENY no POST, O-ENF after verify, O-ORD call order."""

from __future__ import annotations

import pytest

from core.domain.attachment_ref import AttachmentRef
from core.domain.errors import (
    DepthExceededError,
    LegalFloorError,
    MediaTypeNotAllowedError,
    ReactionDisabledError,
    WriteDeniedError,
)
from core.domain.knobs import FixedThreadKnobs
from core.domain.reaction_mark import ReactionMark, ReactionTarget
from core.domain.thread_key import ThreadKey
from tc02_orch_fixtures import default_knobs, make_orch_harness, patch_gateway
from threadcontext_fixtures import SAMPLE_ISSUE_ID


def _key() -> ThreadKey:
    return ThreadKey(node="n1", entity_type="Issue", entity_id="e1")


@pytest.mark.parametrize(
    ("kind", "scenario_id"),
    [
        ("comment", "O-DENY-comment"),
        ("reaction", "O-DENY-reaction"),
        ("attachment", "O-DENY-attachment"),
    ],
)
def test_o_deny_no_post_to_fake_postgrest(kind: str, scenario_id: str) -> None:
    harness = make_orch_harness(backend="supabase_stub", verified=False)
    key = _key()
    with patch_gateway(harness.mock_http), pytest.raises(WriteDeniedError):
        if kind == "comment":
            harness.orchestrator.write_comment("tok", SAMPLE_ISSUE_ID, key, "nope")
        elif kind == "reaction":
            harness.orchestrator.write_reaction(
                "tok",
                SAMPLE_ISSUE_ID,
                ReactionMark(
                    actor_id="a1",
                    target=ReactionTarget(kind="thread_root", thread_key=key),
                    reaction_id="acknowledge",
                ),
            )
        else:
            harness.orchestrator.write_attachment_ref(
                "tok",
                SAMPLE_ISSUE_ID,
                AttachmentRef(ref_id="blob://ok", media_type="image/png", comment_id="c1"),
            )
    assert harness.fake is not None
    assert harness.fake.posts() == []
    assert not any(method == "POST" for method, _ in harness.fake.calls)
    assert scenario_id.startswith("O-DENY-")


def test_o_enf_depth_after_verify() -> None:
    """O-ENF-depth"""
    knobs = FixedThreadKnobs(max_depth=1, max_reactions_per_actor=3, media_allowed_types=("image/png",))
    harness = make_orch_harness(backend="supabase_stub", verified=True, knobs=knobs)
    key = _key()
    with patch_gateway(harness.mock_http):
        root = harness.orchestrator.write_comment("tok", SAMPLE_ISSUE_ID, key, "d1")
        with pytest.raises(DepthExceededError):
            harness.orchestrator.write_comment(
                "tok", SAMPLE_ISSUE_ID, key, "d2", parent_id=root.comment_id
            )
    assert harness.fake is not None
    comment_posts = [path for method, path in harness.fake.posts() if path.endswith("thread_comments")]
    assert len(comment_posts) == 1


def test_o_enf_enable_after_verify() -> None:
    """O-ENF-enable"""
    knobs = FixedThreadKnobs(
        max_depth=3,
        max_reactions_per_actor=3,
        reactions_enable={"acknowledge": True, "amused": False},
        media_allowed_types=("image/png",),
    )
    harness = make_orch_harness(backend="supabase_stub", verified=True, knobs=knobs)
    key = _key()
    with patch_gateway(harness.mock_http), pytest.raises(ReactionDisabledError):
        harness.orchestrator.write_reaction(
            "tok",
            SAMPLE_ISSUE_ID,
            ReactionMark(
                actor_id="a1",
                target=ReactionTarget(kind="thread_root", thread_key=key),
                reaction_id="amused",
            ),
        )
    assert harness.fake is not None
    assert not any(path.endswith("thread_reaction_marks") and method == "POST" for method, path in harness.fake.calls)


def test_o_enf_allowlist_after_verify() -> None:
    """O-ENF-allowlist"""
    harness = make_orch_harness(backend="supabase_stub", verified=True, knobs=default_knobs())
    with patch_gateway(harness.mock_http), pytest.raises(MediaTypeNotAllowedError):
        harness.orchestrator.write_attachment_ref(
            "tok",
            SAMPLE_ISSUE_ID,
            AttachmentRef(ref_id="blob://vid", media_type="video/mp4", comment_id="c1"),
        )
    assert harness.fake is not None
    assert not any(path.endswith("thread_attachment_refs") and method == "POST" for method, path in harness.fake.calls)


def test_o_enf_floor_after_verify() -> None:
    """O-ENF-floor"""
    harness = make_orch_harness(backend="supabase_stub", verified=True)
    with patch_gateway(harness.mock_http), pytest.raises(LegalFloorError):
        harness.orchestrator.write_attachment_ref(
            "tok",
            SAMPLE_ISSUE_ID,
            AttachmentRef(
                ref_id="blob://csam",
                media_type="image/png",
                comment_id="c1",
                floor_class="csam",
            ),
        )
    assert harness.fake is not None
    assert not any(path.endswith("thread_attachment_refs") and method == "POST" for method, path in harness.fake.calls)


@pytest.mark.parametrize("backend", ("in_memory", "supabase_stub"))
def test_o_ord_pull_then_verify_then_persist(backend: str) -> None:
    scenario_id = f"O-ORD-{backend}"
    harness = make_orch_harness(backend=backend, verified=True)  # type: ignore[arg-type]
    key = _key()
    with patch_gateway(harness.mock_http):
        comment = harness.orchestrator.write_comment("tok", SAMPLE_ISSUE_ID, key, "hello")
    assert comment.body == "hello"
    assert harness.order[0] == "gw"
    assert "me" in harness.order
    assert harness.order.index("gw") < harness.order.index("me")
    if backend == "supabase_stub":
        assert "db" in harness.order
        assert harness.order.index("me") < harness.order.index("db")
        assert harness.fake is not None
        assert harness.fake.posts()
    else:
        assert harness.discussion.list_comments(key) == [comment]
        assert "db" not in harness.order
    urls = [call.args[1] for call in harness.mock_http.request.call_args_list]
    assert any("/node/issues/" in url for url in urls)
    assert any(url.endswith("/node/shell-settings") for url in urls)
    harness.me.fetch_me.assert_called_with("tok")
    assert scenario_id.startswith("O-ORD-")
