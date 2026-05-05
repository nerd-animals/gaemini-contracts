"""OHLCV Parquet column schema and partition policy.

Producer
    gaemini-data (collector). Writes one Parquet file per
    (market, ticker, KST date).

Consumers
    gaemini-core  — strategy data loader.
    gaemini-view  — chart rendering.

Both writer and reader compute the partition key the same way:
    1. Parse the ``date`` column as datetime.
    2. Localize naive timestamps as UTC.
    3. Convert to ``Asia/Seoul``.
    4. Format ``%Y-%m-%d`` for the file name.

Example files (paths via ``keys/parquet_path.py``)
    ``/cache/crypto/KRW-BTC/2026-05-03.parquet``       — daily bars
    ``/cache/crypto/KRW-BTC_1m/2026-05-03.parquet``    — 1-minute bars

Sample rows (in canonical column order)::

    date                  open       high       low        close      volume
    "2026-05-03"          50_000_000 51_200_000 49_800_000 50_900_000  123.4
    "2026-05-03 09:01"    50_010_000 50_050_000 49_990_000 50_030_000    1.2
"""
from __future__ import annotations

OHLCV_COLUMNS: tuple[str, ...] = (
    "date",     # str — see format note in the docstring below
    "open",     # float — opening price of the bar (quote-asset units)
    "high",     # float — highest traded price during the bar
    "low",      # float — lowest traded price during the bar
    "close",    # float — last traded price of the bar
    "volume",   # float — base-asset volume traded during the bar
)
"""Canonical column order for OHLCV Parquet partitions.

``date`` is a string in one of two formats:
    ``YYYY-MM-DD``        — daily bars        e.g. "2026-05-03"
    ``YYYY-MM-DD HH:MM``  — intraday minute bars  e.g. "2026-05-03 09:01"

Strings (rather than pandas Timestamp) keep Parquet/Arrow columns portable
across language runtimes and stable across schema versions.
"""

PARTITION_TIMEZONE = "Asia/Seoul"
"""KST (UTC+9). Partition file boundaries are KST midnight, NOT UTC midnight.

Rationale: trading days for KRX (and most KR-resident operators) are
Asia/Seoul-aligned. Parquet file ``2026-05-03.parquet`` contains all bars
whose KST calendar day is 2026-05-03, regardless of UTC date.
"""

PARTITION_GRANULARITY = "day"
"""One Parquet file per (market, ticker, KST date)."""

MINUTE_SYMBOL_SUFFIX = "_1m"
"""Suffix appended to the ticker for 1-minute bars.

    KRW-BTC daily bars  →  ``crypto/KRW-BTC/...``
    KRW-BTC 1-min bars  →  ``crypto/KRW-BTC_1m/...``

Keeps the path helper simple (one symbol = one directory) while supporting
multiple intervals per logical ticker.
"""
