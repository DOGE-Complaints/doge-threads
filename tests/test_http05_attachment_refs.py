"""t01–t03 — POST /threads/issues/{issue_id}/attachment-refs + floor/allowlist."""

from __future__ import annotations

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from core.api.asgi_app import app, get_api_dependencies
from core.api.dependencies import ApiDependencies
from core.config import load_config_from_env
from threadcontext_fixtures import SAMPLE_ISSUE_ID
from write_orchestrator_fixtures import make_orchestrator, patch_gateway

_PATH = f"/threads/issues/{SAMPLE_ISSUE_ID}/attachment-refs"
_HEADERS = {"Authorization": "Bearer user-tok"}


def _deps(*, verified: bool) -> tuple[ApiDependencies, object]:
    orch, store, _marks, _refs, mock_http, me = make_orchestrator(verified=verified)
    config = load_config_from_env(
        {
            "APP_PROFILE": "demo",
            "DB_BACKEND": "in_memory",
            "DOGESTONIA_SCHEMA_ID": "uus_veerenni_civic",
            "GATEWAY_BASE_URL": "https://gateway.example",
        }
    )
    deps = ApiDependencies(
        config=config,
        write_orchestrator=orch,
        discussion_store=store,
        thread_knobs=store.knobs,
        identity_me=me,
        gateway=orch._gateway,
    )
    return deps, mock_http


@pytest.fixture
def attach_env() -> Iterator[tuple[TestClient, object]]:
    deps, mock_http = _deps(verified=True)
    app.dependency_overrides[get_api_dependencies] = lambda: deps
    try:
        yield TestClient(app), mock_http
    finally:
        app.dependency_overrides.clear()


def _body(
    *,
    media_type: str = "image/png",
    floor_class: str | None = None,
) -> dict[str, str]:
    payload = {
        "ref_id": "blob://ref-1",
        "media_type": media_type,
        "comment_id": "c-1",
    }
    if floor_class is not None:
        payload["floor_class"] = floor_class
    return payload


def test_missing_bearer_is_401(client: TestClient) -> None:
    response = client.post(_PATH, json=_body())
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "UNAUTHORIZED"


def test_unverified_bearer_is_403() -> None:
    deps, _mock_http = _deps(verified=False)
    app.dependency_overrides[get_api_dependencies] = lambda: deps
    try:
        response = TestClient(app).post(_PATH, json=_body(), headers=_HEADERS)
    finally:
        app.dependency_overrides.clear()
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "FORBIDDEN"


def test_happy_ref(attach_env: tuple[TestClient, object]) -> None:
    client, mock_http = attach_env
    with patch_gateway(mock_http):
        response = client.post(_PATH, json=_body(), headers=_HEADERS)
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["ref_id"] == "blob://ref-1"
    assert data["media_type"] == "image/png"
    assert data["comment_id"] == "c-1"
    assert data["floor_class"] == "ok"


def test_allowlist_deny(attach_env: tuple[TestClient, object]) -> None:
    client, mock_http = attach_env
    with patch_gateway(mock_http):
        response = client.post(
            _PATH, json=_body(media_type="application/pdf"), headers=_HEADERS
        )
    assert response.status_code == 200
    error = response.json()["error"]
    assert error["code"] == "DOMAIN_ERROR"
    assert error["details"]["reason"] == "attach-denied"


def test_floor_deny(attach_env: tuple[TestClient, object]) -> None:
    client, mock_http = attach_env
    with patch_gateway(mock_http):
        response = client.post(
            _PATH, json=_body(floor_class="csam"), headers=_HEADERS
        )
    assert response.status_code == 200
    error = response.json()["error"]
    assert error["code"] == "DOMAIN_ERROR"
    assert error["details"]["reason"] == "attach-denied"


def test_no_blob_or_multipart_route() -> None:
    asgi = (
        __import__("pathlib").Path(__file__).resolve().parents[1]
        / "src"
        / "core"
        / "api"
        / "asgi_app.py"
    ).read_text(encoding="utf-8")
    assert "multipart" not in asgi.lower()
    assert "UploadFile" not in asgi
    assert "/bytes" not in asgi
    assert "/blob" not in asgi
