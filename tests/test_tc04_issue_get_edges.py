"""t01 — C-GW-ISS-* Issue get httpx edges (offline stubs, no live)."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from core.application.pull_thread_context import ISSUE_GET_PATH_TEMPLATE, pull_issue_projection
from core.domain.errors import ThreadContextError
from core.gateway.client import GatewayClientError
from tc04_httpx_fixtures import stub_gateway_http
from threadcontext_fixtures import SAMPLE_ISSUE_ID


@pytest.mark.parametrize(
    ("status_code", "scenario_id"),
    [
        (404, "C-GW-ISS-404"),
        (500, "C-GW-ISS-500"),
    ],
)
def test_c_gw_iss_http_status(status_code: int, scenario_id: str) -> None:
    client, mock_http = stub_gateway_http(status_code=status_code)
    with patch("core.gateway.client.httpx.Client", return_value=mock_http):
        with pytest.raises(GatewayClientError, match=f"HTTP {status_code}"):
            pull_issue_projection(client, SAMPLE_ISSUE_ID)
    path = ISSUE_GET_PATH_TEMPLATE.format(issue_id=SAMPLE_ISSUE_ID)
    assert mock_http.request.call_args.args[0] == "GET"
    assert mock_http.request.call_args.args[1].endswith(path)
    assert scenario_id.startswith("C-GW-ISS-")


def test_c_gw_iss_timeout() -> None:
    """C-GW-ISS-timeout"""
    client, mock_http = stub_gateway_http(timeout=True)
    with patch("core.gateway.client.httpx.Client", return_value=mock_http):
        with pytest.raises(GatewayClientError, match="timed out"):
            pull_issue_projection(client, SAMPLE_ISSUE_ID)


def test_c_gw_iss_bad_json() -> None:
    """C-GW-ISS-bad-json — invalid JSON bubbles from response.json (documented)."""
    client, mock_http = stub_gateway_http(json_error=ValueError("not json"))
    with patch("core.gateway.client.httpx.Client", return_value=mock_http):
        with pytest.raises(ValueError, match="not json"):
            pull_issue_projection(client, SAMPLE_ISSUE_ID)


def test_c_gw_iss_missing_issue() -> None:
    """C-GW-ISS-missing-issue"""
    client, mock_http = stub_gateway_http(payload={"not_issue": {}})
    with patch("core.gateway.client.httpx.Client", return_value=mock_http):
        with pytest.raises(ThreadContextError, match="issue projection missing"):
            pull_issue_projection(client, SAMPLE_ISSUE_ID)
