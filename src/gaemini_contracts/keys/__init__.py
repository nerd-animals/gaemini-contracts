"""File path helpers for cross-repo data files.

Producers (writers) and consumers (readers) both call these helpers, so the
on-disk layout stays in sync — no raw f-strings sprinkled around the codebase.

Coverage
    OHLCV Parquet  — ``parquet_path``, ``parquet_market_dir``, ``parquet_ticker_dir``
    Application logs — ``log_path``, ``log_instance_dir``, ``log_strategy_dir``
    Trade logs       — ``trade_log_path``, ``trades_dir``
"""
from gaemini_contracts.keys.log_path import (
    log_instance_dir,
    log_path,
    log_strategy_dir,
)
from gaemini_contracts.keys.parquet_path import (
    parquet_market_dir,
    parquet_path,
    parquet_ticker_dir,
)
from gaemini_contracts.keys.trade_log_path import (
    trade_log_path,
    trades_dir,
)

__all__ = [
    "log_path",
    "log_instance_dir",
    "log_strategy_dir",
    "parquet_path",
    "parquet_market_dir",
    "parquet_ticker_dir",
    "trade_log_path",
    "trades_dir",
]
