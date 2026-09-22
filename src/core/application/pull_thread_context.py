from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from core.application.compose_thread_context import ThreadContextComposer
from core.domain.errors import ThreadContextError
from core.domain.story_narrative import assert_no_story_narrative
from core.domain.thread_context import IssueProjection, ThreadContext, parse_issue_projection
from core.gateway.client import GatewayClient, GatewayClientError

ISSUE_GET_PATH_TEMPLATE = "/node/issues/{issue_id}"
SHELL_SETTINGS_PATH = "/node/shell-settings"


def _json_payload(response: Any, *, path: str) -> Mapping[str, Any]:
    status = int(getattr(response, "status_code", 0) or 0)
    if status >= 400:
        raise GatewayClientError(f"Gateway {path} returned HTTP {status}")
    payload = response.json()
    if not isinstance(payload, Mapping):
        raise ThreadContextError(f"Gateway {path} returned a non-object body")
    return payload


def pull_issue_projection(client: GatewayClient, issue_id: str) -> IssueProjection:
    """Pull civic Issue get via existing GatewayClient. Path caller-supplied."""
    path = ISSUE_GET_PATH_TEMPLATE.format(issue_id=issue_id)
    payload = _json_payload(client.request("GET", path), path=path)
    assert_no_story_narrative(payload)
    return parse_issue_projection(payload, fallback_issue_id=issue_id)


def pull_pack_shell_settings(client: GatewayClient) -> Mapping[str, Any]:
    """Pull service-auth GET /node/shell-settings (headers from GatewayClient)."""
    payload = _json_payload(
        client.request("GET", SHELL_SETTINGS_PATH),
        path=SHELL_SETTINGS_PATH,
    )
    assert_no_story_narrative(payload)
    if "pack_shell_settings" not in payload:
        raise ThreadContextError("pack_shell_settings missing")
    return payload


def pull_and_compose(client: GatewayClient, issue_id: str) -> ThreadContext:
    """Pull Issue + shell settings and compose ThreadContext in threads."""
    issue = pull_issue_projection(client, issue_id)
    settings = pull_pack_shell_settings(client)
    return ThreadContextComposer().compose(issue, settings)
