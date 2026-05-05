"""OHLCV Parquet schema — column order and partition policy.

The single source of truth for the on-disk OHLCV format that
gaemini-data writes and gaemini-core / gaemini-view read.
"""
from gaemini_contracts.schema.ohlcv import (
    MINUTE_SYMBOL_SUFFIX,
    OHLCV_COLUMNS,
    PARTITION_GRANULARITY,
    PARTITION_TIMEZONE,
)

__all__ = [
    "MINUTE_SYMBOL_SUFFIX",
    "OHLCV_COLUMNS",
    "PARTITION_GRANULARITY",
    "PARTITION_TIMEZONE",
]
