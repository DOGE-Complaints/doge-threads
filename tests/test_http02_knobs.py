"""t01/t04 — GET /threads/knobs snapshot + U1 capacity ≥3."""

from __future__ import annotations

from fastapi.testclient import TestClient


def test_get_knobs_arch_minimum_fields(client: TestClient) -> None:
    response = client.get("/threads/knobs")
    assert response.status_code == 200
    body = response.json()
    data = body["data"]
    assert "trace_id" in body
    assert data["max_depth"] == 8
    assert data["max_reactions_per_actor"] >= 3
    assert data["reactions_enable"] == {}
    assert data["media_allowed_types"] == []
    assert "issue_id" not in data
    assert "knobs" not in data
