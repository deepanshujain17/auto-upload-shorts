import logging
import os
from typing import Any, Dict, Optional


class _KeyValueFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        base = super().format(record)
        extra: Optional[Dict[str, Any]] = getattr(record, "extra_fields", None)
        if not extra:
            return base
        suffix = " ".join(f"{k}={extra[k]!r}" for k in sorted(extra.keys()))
        return f"{base} {suffix}"


def configure_logging(level: Optional[str] = None) -> None:
    """
    Configure stdlib logging once for the whole app.
    """
    resolved_level = (level or os.getenv("LOG_LEVEL") or "INFO").upper()
    root = logging.getLogger()
    if root.handlers:
        root.setLevel(resolved_level)
        return

    handler = logging.StreamHandler()
    handler.setFormatter(
        _KeyValueFormatter(
            fmt="%(asctime)s %(levelname)s %(name)s - %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S",
        )
    )
    root.addHandler(handler)
    root.setLevel(resolved_level)


def get_logger(name: str, **context: Any) -> logging.LoggerAdapter:
    base = logging.getLogger(name)
    return logging.LoggerAdapter(base, {"extra_fields": context})


def with_context(logger: logging.LoggerAdapter, **context: Any) -> logging.LoggerAdapter:
    merged = dict(getattr(logger, "extra", {}).get("extra_fields", {}))
    merged.update(context)
    return logging.LoggerAdapter(logger.logger, {"extra_fields": merged})
