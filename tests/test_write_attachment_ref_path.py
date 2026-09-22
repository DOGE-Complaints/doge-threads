from __future__ import annotations

import pytest

from core.domain.attachment_ref import AttachmentRef
from core.domain.errors import LegalFloorError, MediaTypeNotAllowedError, WriteDeniedError
from threadcontext_fixtures import SAMPLE_ISSUE_ID
from write_orchestrator_fixtures import make_orchestrator, patch_gateway


def test_attachment_ref_write_allowlist_and_floor() -> None:
    orch, _store, _marks, refs, mock_http, me = make_orchestrator(verified=True)
    ref = AttachmentRef(ref_id="blob://ok", media_type="image/png", comment_id="c1")
    with patch_gateway(mock_http):
        stored = orch.write_attachment_ref("tok", SAMPLE_ISSUE_ID, ref)
    assert stored == ref
    assert refs.list_refs("c1") == [ref]
    me.fetch_me.assert_called_once_with("tok")


def test_attachment_ref_out_of_policy_and_floor() -> None:
    orch, _store, _marks, refs, mock_http, _me = make_orchestrator(verified=True)
    with patch_gateway(mock_http), pytest.raises(MediaTypeNotAllowedError):
        orch.write_attachment_ref(
            "tok",
            SAMPLE_ISSUE_ID,
            AttachmentRef(ref_id="blob://vid", media_type="video/mp4", comment_id="c1"),
        )
    with patch_gateway(mock_http), pytest.raises(LegalFloorError):
        orch.write_attachment_ref(
            "tok",
            SAMPLE_ISSUE_ID,
            AttachmentRef(
                ref_id="blob://csam",
                media_type="image/png",
                comment_id="c1",
                floor_class="csam",
            ),
        )
    assert refs.list_refs("c1") == []


def test_attachment_ref_denied() -> None:
    orch, _store, _marks, refs, mock_http, _me = make_orchestrator(verified=False)
    with patch_gateway(mock_http), pytest.raises(WriteDeniedError):
        orch.write_attachment_ref(
            "tok",
            SAMPLE_ISSUE_ID,
            AttachmentRef(ref_id="blob://ok", media_type="image/png", comment_id="c1"),
        )
    assert refs.list_refs("c1") == []
