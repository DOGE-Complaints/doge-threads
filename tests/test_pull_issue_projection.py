from __future__ import annotations

from unittest.mock import patch

import pytest

from core.application.pull_thread_context import pull_issue_projection
from core.domain.errors import StoryNarrativeError
from threadcontext_fixtures import (
    SAMPLE_ISSUE_ID,
    SAMPLE_ISSUE_PAYLOAD,
    SAMPLE_STORY_ID,
    stub_gateway_client,
)


def test_pull_issue_projection_opaque_ids_only() -> None:
    client, mock_http = stub_gateway_client()
    with patch("core.gateway.client.httpx.Client", return_value=mock_http):
        issue = pull_issue_projection(client, SAMPLE_ISSUE_ID)
    assert issue.issue_id == SAMPLE_ISSUE_ID
    assert issue.opaque_story_ids == (SAMPLE_STORY_ID,)
    mock_http.request.assert_called()
    _method, url = mock_http.request.call_args.args[:2]
    assert _method == "GET"
    assert url == f"https://gateway.example/node/issues/{SAMPLE_ISSUE_ID}"


def test_pull_issue_rejects_story_body() -> None:
    tainted = {
        "issue": {
            "id": SAMPLE_ISSUE_ID,
            "story_ids": [SAMPLE_STORY_ID],
            "story_body": "narrative must not land",
        }
    }
    client, mock_http = stub_gateway_client(issue_payload=tainted)
    with patch("core.gateway.client.httpx.Client", return_value=mock_http):
        with pytest.raises(StoryNarrativeError):
            pull_issue_projection(client, SAMPLE_ISSUE_ID)
    assert SAMPLE_ISSUE_PAYLOAD["issue"]["id"] == SAMPLE_ISSUE_ID
