"""LogRecord — one JSONL row written by gaemini-core, read by gaemini-view.

File path: `{log_root}/{instance}/{strategy}/{date}.jsonl` (see keys/log_path.py).
Top-level schema_version (B6) — view fails fast on mismatch.
"""
from __future__ import annotations

from typing import Any, TypedDict

LOG_RECORD_VERSION = 1


class LogRecord(TypedDict):
    schema_version: int
    ts: str  # UTC ISO 8601
    level: str  # "DEBUG" | "INFO" | "WARNING" | "ERROR"
    source: str  # "strategy" | "system"
    tick_id: str | None
    message: str
    extra: dict[str, Any]
