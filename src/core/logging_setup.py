from __future__ import annotations

import logging
import sys
from contextvars import ContextVar

_current_trace_id: ContextVar[str | None] = ContextVar("trace_id", default=None)
_current_story_id: ContextVar[str | None] = ContextVar("story_id", default=None)


class _ContextDefaultsFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        if not hasattr(record, "trace_id"):
            record.trace_id = _current_trace_id.get() or "-"
        if not hasattr(record, "story_id"):
            record.story_id = _current_story_id.get() or "-"
        return True


class _LevelBelowWarningFilter(logging.Filter):
    """Pass only DEBUG/INFO records for stdout split stream."""

    def filter(self, record: logging.LogRecord) -> bool:
        return record.levelno < logging.WARNING


def configure_logging(
    log_level: str, *, log_format: str = "text", log_debug_dir: str | None = None
) -> None:
    # log_debug_dir is accepted for AppConfig symmetry; files are not written here.
    del log_debug_dir
    level = getattr(logging, log_level.upper(), logging.INFO)
    if log_format.strip().lower() == "json":
        fmt = (
            '{"ts":"%(asctime)s","level":"%(levelname)s","logger":"%(name)s",'
            '"msg":"%(message)s","trace_id":"%(trace_id)s","story_id":"%(story_id)s"}'
        )
    else:
        fmt = (
            "%(asctime)s %(levelname)-8s %(name)s %(message)s "
            "[trace_id=%(trace_id)s story_id=%(story_id)s]"
        )

    root = logging.getLogger()
    root.setLevel(level)
    for handler in list(root.handlers):
        root.removeHandler(handler)

    formatter = logging.Formatter(fmt)

    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(level)
    stdout_handler.addFilter(_LevelBelowWarningFilter())
    stdout_handler.setFormatter(formatter)
    stdout_handler.addFilter(_ContextDefaultsFilter())
    root.addHandler(stdout_handler)

    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setLevel(logging.WARNING)
    stderr_handler.setFormatter(formatter)
    stderr_handler.addFilter(_ContextDefaultsFilter())
    root.addHandler(stderr_handler)

    logging.getLogger("uvicorn.access").propagate = False
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger(__name__).info(
        "logging.configured",
        extra={
            "configured_level": log_level.upper(),
            "log_format": log_format.lower(),
        },
    )
