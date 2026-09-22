"""t02 — C-GW-SET-* shell-settings httpx + story-key matrix (offline, no live)."""

from __future__ import annotations

from copy import deepcopy
from unittest.mock import patch

import pytest

from core.application.pull_thread_context import (
    SHELL_SETTINGS_PATH,
    pull_and_compose,
    pull_pack_shell_settings,
)
from core.domain.errors import StoryNarrativeError, ThreadContextError
from core.domain.story_narrative import FORBIDDEN_STORY_KEYS
from core.gateway.client import GatewayClientError
from tc04_httpx_fixtures import stub_gateway_http
from threadcontext_fixtures import SAMPLE_ISSUE_ID, SAMPLE_SETTINGS_PAYLOAD

_FORBIDDEN_IDS = {
    "story": "C-GW-SET-forbidden-story",
    "stories": "C-GW-SET-forbidden-stories",
    "story_body": "C-GW-SET-forbidden-story_body",
    "narrative": "C-GW-SET-forbidden-narrative",
    "original_text": "C-GW-SET-forbidden-original_text",
    "thread_context": "C-GW-SET-forbidden-thread_context",
    "ThreadContext": "C-GW-SET-forbidden-ThreadContext",
}


def test_c_gw_set_401_without_service_token() -> None:
    """C-GW-SET-401"""
    client, mock_http = stub_gateway_http(status_code=401, service_token=None)
    with patch("core.gateway.client.httpx.Client", return_value=mock_http):
        with pytest.raises(GatewayClientError, match="HTTP 401"):
            pull_pack_shell_settings(client)
    assert mock_http.request.call_args.args[0] == "GET"
    assert mock_http.request.call_args.args[1].endswith(SHELL_SETTINGS_PATH)
    assert mock_http.request.call_args.kwargs["headers"] == {}


@pytest.mark.parametrize("forbidden_key", sorted(FORBIDDEN_STORY_KEYS))
def test_c_gw_set_forbidden_story_keys(forbidden_key: str) -> None:
    scenario_id = _FORBIDDEN_IDS[forbidden_key]
    tainted = deepcopy(SAMPLE_SETTINGS_PAYLOAD)
    tainted["pack_shell_settings"][forbidden_key] = "must-reject"
    client, mock_http = stub_gateway_http(payload=tainted)
    with patch("core.gateway.client.httpx.Client", return_value=mock_http):
        with pytest.raises(StoryNarrativeError):
            pull_pack_shell_settings(client)
    assert scenario_id == f"C-GW-SET-forbidden-{forbidden_key}"
    assert set(_FORBIDDEN_IDS) == set(FORBIDDEN_STORY_KEYS)


def test_c_gw_set_incomplete_pack_fail_closed() -> None:
    """C-GW-SET-incomplete-pack"""
    client, mock_http = stub_gateway_http(payload={})
    with patch("core.gateway.client.httpx.Client", return_value=mock_http):
        with pytest.raises(ThreadContextError, match="pack_shell_settings missing"):
            pull_pack_shell_settings(client)


def test_c_gw_set_incomplete_threads_fail_closed() -> None:
    """C-GW-SET-incomplete-threads"""
    payload = {
        "issue": {"id": SAMPLE_ISSUE_ID, "story_ids": []},
        "pack_shell_settings": {},
    }
    client, mock_http = stub_gateway_http(payload=payload)
    with patch("core.gateway.client.httpx.Client", return_value=mock_http):
        with pytest.raises(ThreadContextError, match="threads missing"):
            pull_and_compose(client, SAMPLE_ISSUE_ID)
