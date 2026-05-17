"""디스크 Parquet 스키마 — 컬럼 순서·dtype·파티션 정책.

gaemini-data가 쓰고 gaemini-core / gaemini-view가 읽는 디스크 포맷의
단일 진실 공급원 (single source of truth).

    OHLCV  — ``schema.ohlcv`` (집계 시세 봉)
    이벤트  — ``schema.event`` (체결·호가·티커·펀딩·OI 고빈도 이벤트)
"""
from gaemini_contracts.schema.event import (
    EVENT_JOIN_KEY,
    EVENT_KINDS,
    EVENT_PARTITION_GRANULARITY,
    EVENT_PARTITION_KEY,
    EVENT_SCHEMA_VERSION,
    EVENT_SCHEMAS,
    EVENT_TIMESTAMP_FORMAT,
    EventSchema,
)
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
    "EVENT_JOIN_KEY",
    "EVENT_KINDS",
    "EVENT_PARTITION_GRANULARITY",
    "EVENT_PARTITION_KEY",
    "EVENT_SCHEMA_VERSION",
    "EVENT_SCHEMAS",
    "EVENT_TIMESTAMP_FORMAT",
    "EventSchema",
]
