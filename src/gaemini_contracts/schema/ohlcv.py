"""Canonical OHLCV Parquet schema.

Both gaemini-data (collector writer) and gaemini-core / gaemini-view (readers)
must agree on this column ordering and partition policy.
"""
from __future__ import annotations

OHLCV_COLUMNS: tuple[str, ...] = (
    "date",
    "open",
    "high",
    "low",
    "close",
    "volume",
)
"""Canonical column order for OHLCV Parquet partitions.

`date` is a string in one of these formats:
- `YYYY-MM-DD` for daily bars
- `YYYY-MM-DD HH:MM` for intraday minute bars

Strings rather than pandas Timestamp because Parquet/Arrow string
columns are portable across language runtimes and schema_version-stable.
"""

PARTITION_TIMEZONE = "Asia/Seoul"
"""KST (UTC+9). Partition file boundaries are KST midnight, not UTC.

Rationale: trading days for KRX (and most KR-resident operators) are
Asia/Seoul-aligned. Parquet file `2026-05-03.parquet` contains all bars
whose KST calendar day is 2026-05-03, regardless of UTC date.

Both writer and reader compute the partition key the same way:
1. Parse `date` column as datetime
2. Localize naive timestamps as UTC
3. Convert to Asia/Seoul
4. Format as `%Y-%m-%d`
"""

PARTITION_GRANULARITY = "day"
"""One Parquet file per (market, ticker, KST date)."""

MINUTE_SYMBOL_SUFFIX = "_1m"
"""1-minute bars are stored under `{ticker}{MINUTE_SYMBOL_SUFFIX}` symbol.

For example, KRW-BTC daily bars live under `crypto/KRW-BTC/`, while
1-minute bars live under `crypto/KRW-BTC_1m/`. This keeps the path
helper simple (one symbol = one directory) while supporting multiple
intervals per logical ticker.
"""
