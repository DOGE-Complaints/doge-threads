"""t03 — H-TR TRACEABILITY.md matrix + 9.5 rubric."""

from __future__ import annotations

import re
from pathlib import Path

from tc01_traceability import TC01_SCENARIO_IDS
from tc02_traceability import TC02_SCENARIO_IDS
from tc03_traceability import TC03_SCENARIO_IDS
from tc04_traceability import TC04_SCENARIO_IDS
from tc05_traceability import TC05_SCENARIO_IDS
from tc06_traceability import TC06_SCENARIO_IDS
from tc07_traceability import TC07_SCENARIO_IDS
from tc08_traceability import TC08_SCENARIO_IDS
from tc09_traceability import TC09_SCENARIO_IDS

_TRACE = (
    Path(__file__).resolve().parents[1]
    / "docs"
    / "tasks"
    / "backlog-stories"
    / "req01-test-hardening"
    / "TRACEABILITY.md"
)

_ALL_PRIOR = (
    TC01_SCENARIO_IDS
    | TC02_SCENARIO_IDS
    | TC03_SCENARIO_IDS
    | TC04_SCENARIO_IDS
    | TC05_SCENARIO_IDS
    | TC06_SCENARIO_IDS
    | TC07_SCENARIO_IDS
    | TC08_SCENARIO_IDS
)


def test_h_tr_matrix_lists_all_tc01_08_ids() -> None:
    assert "H-TR-matrix" in TC09_SCENARIO_IDS
    assert _TRACE.is_file()
    text = _TRACE.read_text(encoding="utf-8")
    missing = sorted(item for item in _ALL_PRIOR if f"`{item}`" not in text)
    assert missing == []
    pending_or_pass = re.findall(r"\| (pass|pending) \|", text)
    assert pending_or_pass


def test_h_tr_rubric_9_5() -> None:
    assert "H-TR-rubric-9-5" in TC09_SCENARIO_IDS
    text = _TRACE.read_text(encoding="utf-8")
    assert "9.5" in text
    assert "≥90%" in text or ">=90%" in text
    assert "offline" in text.lower()
