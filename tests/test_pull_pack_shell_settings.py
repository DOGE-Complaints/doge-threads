from __future__ import annotations

from unittest.mock import patch

from core.application.pull_thread_context import pull_and_compose, pull_pack_shell_settings
from threadcontext_fixtures import SAMPLE_ISSUE_ID, SAMPLE_SETTINGS_PAYLOAD, stub_gateway_client


def test_pull_shell_settings_uses_service_headers() -> None:
    client, mock_http = stub_gateway_client()
    with patch("core.gateway.client.httpx.Client", return_value=mock_http):
        payload = pull_pack_shell_settings(client)
    assert payload["pack_shell_settings"]["threads"]["tree"]["max_depth"] == 3
    settings_call = next(
        call
        for call in mock_http.request.call_args_list
        if call.args[1].endswith("/node/shell-settings")
    )
    assert settings_call.args[0] == "GET"
    assert settings_call.kwargs["headers"] == {
        "Authorization": "Bearer svc",
        "X-Service-Token": "svc",
    }


def test_pull_and_compose_offline_stub() -> None:
    client, mock_http = stub_gateway_client()
    with patch("core.gateway.client.httpx.Client", return_value=mock_http):
        context = pull_and_compose(client, SAMPLE_ISSUE_ID)
    assert context.issue.issue_id == SAMPLE_ISSUE_ID
    assert context.knobs.max_depth == SAMPLE_SETTINGS_PAYLOAD["pack_shell_settings"][
        "threads"
    ]["tree"]["max_depth"]
    paths = {call.args[1] for call in mock_http.request.call_args_list}
    assert any("/node/issues/" in path for path in paths)
    assert any(path.endswith("/node/shell-settings") for path in paths)
