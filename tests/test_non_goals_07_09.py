from __future__ import annotations

from pathlib import Path


_SRC_ROOT = Path(__file__).resolve().parents[1] / "src"
_FORBIDDEN = (
    "vote_storage",
    "sanction_signal",
    "cabinet_metric",
    "drift_scor",
    "rate_limit",
    "near_dup",
    "near-duplicate",
)


def test_ac_thr_07_09_non_goals_absent_from_src() -> None:
    hits: list[str] = []
    for path in _SRC_ROOT.rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        for token in _FORBIDDEN:
            if token in text:
                hits.append(f"{path.relative_to(_SRC_ROOT)}:{token}")
    assert hits == []
