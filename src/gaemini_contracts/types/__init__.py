"""JSONL record schemas for cross-repo log files.

Each record carries a top-level ``schema_version`` so readers can fail fast
on mismatch via :func:`gaemini_contracts.versioning.parse_versioned_json`.

Coverage
    LogRecord    — application logs (core writes, view reads).
    TradeRecord  — trade fill events (core writes, view reads).
"""
from gaemini_contracts.types.log_record import LOG_RECORD_VERSION, LogRecord
from gaemini_contracts.types.trade_record import TRADE_RECORD_VERSION, TradeRecord

__all__ = [
    "LOG_RECORD_VERSION",
    "LogRecord",
    "TRADE_RECORD_VERSION",
    "TradeRecord",
]
