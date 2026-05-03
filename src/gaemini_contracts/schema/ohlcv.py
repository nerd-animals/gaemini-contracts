"""Canonical OHLCV Parquet schema.

Both gaemini-data (collector writer) and gaemini-core / gaemini-view (readers)
must agree on this column ordering and partition policy.
"""
from __future__ import annotations

OHLCV_COLUMNS: tuple[str, ...] = (
    "timestamp",
    "open",
    "high",
    "low",
    "close",
    "volume",
)
"""Canonical column order for OHLCV Parquet partitions."""

TIMESTAMP_TIMEZONE = "UTC"
"""All timestamps inside Parquet files are UTC ISO 8601."""

PARTITION_GRANULARITY = "day"
"""One Parquet file per (market, ticker, UTC date)."""
