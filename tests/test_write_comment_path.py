from __future__ import annotations

import pytest

from core.domain import ThreadKey, WriteDeniedError
from threadcontext_fixtures import SAMPLE_ISSUE_ID
from write_orchestrator_fixtures import make_orchestrator, patch_gateway


def test_comment_write_compose_verify_persist() -> None:
    orch, store, _marks, _refs, mock_http, me = make_orchestrator(verified=True)
    key = ThreadKey(node="n1", entity_type="Issue", entity_id="e1")
    with patch_gateway(mock_http):
        comment = orch.write_comment("tok", SAMPLE_ISSUE_ID, key, "hello")
    assert comment.body == "hello"
    assert store.list_comments(key) == [comment]
    me.fetch_me.assert_called_once_with("tok")
    urls = [call.args[1] for call in mock_http.request.call_args_list]
    assert any("/node/issues/" in url for url in urls)
    assert any(url.endswith("/node/shell-settings") for url in urls)


def test_comment_write_denied_before_persist() -> None:
    orch, store, _marks, _refs, mock_http, _me = make_orchestrator(verified=False)
    key = ThreadKey(node="n1", entity_type="Issue", entity_id="e1")
    with patch_gateway(mock_http), pytest.raises(WriteDeniedError):
        orch.write_comment("tok", SAMPLE_ISSUE_ID, key, "nope")
    assert store.get_thread(key) is None
    assert store.list_comments(key) == []
