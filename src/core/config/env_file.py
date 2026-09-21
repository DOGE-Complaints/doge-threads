"""Minimal `.env` parsing for operator DX (no python-dotenv dependency)."""

from __future__ import annotations

from pathlib import Path
from typing import Mapping, MutableMapping


def merge_dotenv_from_path(
    path: Path,
    target: MutableMapping[str, str],
    *,
    priority: Mapping[str, str],
) -> None:
    """Fill *target* with KEY=value from *path* only for keys absent in *priority*.

    *priority* is typically a snapshot of ``os.environ`` at call time: exported shell
    variables win over file lines. Lines starting with ``#``, blanks, and lines without
    ``=`` are skipped. Values may be wrapped in single or double quotes.
    """
    if not path.is_file():
        return
    fixed = frozenset(priority.keys())
    text = path.read_text(encoding="utf-8")
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        if not key or key in fixed:
            continue
        value = value.strip().strip('"').strip("'")
        target[key] = value


def merge_dotenv_from_cwd(
    target: MutableMapping[str, str],
    *,
    priority: Mapping[str, str],
) -> None:
    merge_dotenv_from_path(Path.cwd() / ".env", target, priority=priority)
