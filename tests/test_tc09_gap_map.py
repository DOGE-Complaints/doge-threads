"""t04 — H-GAP G1–G6 closed/deferred."""

from __future__ import annotations

from pathlib import Path

from tc09_traceability import TC09_SCENARIO_IDS

_TRACE = (
    Path(__file__).resolve().parents[1]
    / "docs"
    / "tasks"
    / "backlog-stories"
    / "req01-test-hardening"
    / "TRACEABILITY.md"
).read_text(encoding="utf-8")


def test_h_gap_closed_ids() -> None:
    assert "H-GAP-g1-g4-g6-closed" in TC09_SCENARIO_IDS
    for gap in ("G1", "G2", "G3", "G4", "G6"):
        assert gap in _TRACE
        assert "**closed**" in _TRACE


def test_h_gap_g5_deferred() -> None:
    assert "H-GAP-g5-deferred" in TC09_SCENARIO_IDS
    assert "G5" in _TRACE
    assert "**deferred**" in _TRACE.lower() or "deferred" in _TRACE.lower()
