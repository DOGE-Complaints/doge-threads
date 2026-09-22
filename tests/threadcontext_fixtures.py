from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock

from core.gateway.client import GatewayClient

SAMPLE_ISSUE_ID = "iss-1"
SAMPLE_STORY_ID = "sid-opaque"

SAMPLE_ISSUE_PAYLOAD: dict[str, Any] = {
    "issue": {
        "id": SAMPLE_ISSUE_ID,
        "story_ids": [SAMPLE_STORY_ID],
    }
}

SAMPLE_SETTINGS_PAYLOAD: dict[str, Any] = {
    "pack_shell_settings": {
        "active_schema": {"schema_id": "node", "schema_version": "1"},
        "verification": {"validation_type": "none", "integration_name": "demo"},
        "threads": {
            "tree": {"max_depth": 3},
            "reactions": {
                "max_reactions_per_actor": 2,
                "enable": {"like": True},
                "min_overlap_to_use": {},
                "catalog_ref": "cat",
            },
            "media": {"allowed_types": ["image/png"]},
        },
    }
}


def fake_json_response(payload: dict[str, Any], *, status_code: int = 200) -> MagicMock:
    response = MagicMock()
    response.status_code = status_code
    response.json.return_value = payload
    return response


def stub_gateway_client(
    *,
    issue_payload: dict[str, Any] | None = None,
    settings_payload: dict[str, Any] | None = None,
) -> tuple[GatewayClient, MagicMock]:
    """Offline GatewayClient: httpx stubbed; service headers still applied."""
    client = GatewayClient(base_url="https://gateway.example", service_token="svc")
    mock_http = MagicMock()
    mock_http.__enter__.return_value = mock_http
    mock_http.__exit__.return_value = False

    def _request(method: str, url: str, **kwargs: Any) -> MagicMock:
        if "/node/issues/" in url:
            return fake_json_response(issue_payload or SAMPLE_ISSUE_PAYLOAD)
        if url.endswith("/node/shell-settings"):
            return fake_json_response(settings_payload or SAMPLE_SETTINGS_PAYLOAD)
        return fake_json_response({})

    mock_http.request.side_effect = _request
    return client, mock_http
