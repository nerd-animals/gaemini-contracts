"""OHLCV Parquet 스키마 — 컬럼 순서와 파티션 정책.

gaemini-data가 쓰고 gaemini-core / gaemini-view가 읽는 디스크 OHLCV 포맷의
단일 진실 공급원 (single source of truth).
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
