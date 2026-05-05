"""LogRecord — one application log line, JSONL append-only.

Producer
    gaemini-core (StrategyLogger). Writes one JSON object per line.

Consumer
    gaemini-view (logs view). Parses each line via
    ``parse_versioned_json(line, LOG_RECORD_VERSION, "LogRecord")``.

File path (see ``keys/log_path.py``)
    ``{log_root}/{instance}/{strategy}/{date}.jsonl``
    e.g. ``/var/log/gaemini/paper-crypto/momentum/2026-05-03.jsonl``

Example line::

    {"schema_version": 1, "ts": "2026-05-03T08:01:30+00:00",
     "level": "INFO", "source": "strategy", "tick_id": "t-42",
     "message": "ran momentum strategy",
     "extra": {"signals": 3, "elapsed_ms": 87}}
"""
from __future__ import annotations

from typing import Any, TypedDict

# Bump on any breaking change to LogRecord (renamed / removed field, narrowed
# type). Readers reject lines whose schema_version does not match this value.
LOG_RECORD_VERSION = 1


class LogRecord(TypedDict):
    schema_version: int

    # UTC timestamp, ISO 8601 format.  e.g. "2026-05-03T08:01:30+00:00"
    ts: str

    # Severity. One of: "DEBUG", "INFO", "WARNING", "ERROR".
    level: str

    # What emitted the log.
    #   "strategy" — user strategy code (BaseStrategy.run or hooks).
    #   "system"   — framework / runtime code (scheduler, broker, etc.).
    source: str

    # The strategy tick this log belongs to. None for logs emitted outside
    # any tick — startup, shutdown, cron-level events.
    tick_id: str | None

    # Human-readable message. Keep structured fields in ``extra``, not here.
    message: str

    # Structured key/value pairs (must be JSON-serializable). Used for
    # filtering / dashboards. Avoid large blobs.
    # e.g. {"strategy": "momentum", "signals": 3, "elapsed_ms": 87}
    extra: dict[str, Any]
