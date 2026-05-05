"""Public contracts surface for Gaemini cross-repo file boundaries.

This package owns the file paths and JSONL/Parquet schemas that
`gaemini-data`, `gaemini-core`, and `gaemini-view` all touch.

Mutable live state (`AccountState`, `StrategySpec`, etc.) is owned by
`gaemini-core` and exposed to `gaemini-view` via Core's HTTP API. Such
state is no longer a cross-repo contract.
"""

from gaemini_contracts.types.log_record import LOG_RECORD_VERSION, LogRecord
from gaemini_contracts.types.trade_record import TRADE_RECORD_VERSION, TradeRecord

__all__ = [
    "LOG_RECORD_VERSION",
    "LogRecord",
    "TRADE_RECORD_VERSION",
    "TradeRecord",
]
