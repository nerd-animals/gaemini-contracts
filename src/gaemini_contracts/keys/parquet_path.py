"""Parquet partition path layout for OHLCV bars.

Producer
    gaemini-data (collector) writes one Parquet file per (market, ticker, day).

Consumers
    gaemini-core  — strategy data loader.
    gaemini-view  — chart rendering.

Canonical layout
    ``{cache_dir}/{market}/{ticker}/{date}.parquet``

Example
    >>> parquet_path(Path("/cache"), "crypto", "KRW-BTC", date(2026, 5, 3))
    PosixPath('/cache/crypto/KRW-BTC/2026-05-03.parquet')

``cache_dir`` is provided by the caller (typically from an env var); this
module only owns the ``{market}/{ticker}/{date}.parquet`` portion.
"""
from __future__ import annotations

from datetime import date as Date
from pathlib import Path


def parquet_path(
    cache_dir: Path,
    market: str,
    ticker: str,
    day: Date,
) -> Path:
    """Path to the Parquet file for one (market, ticker, day)."""
    return cache_dir / market / ticker / f"{day.isoformat()}.parquet"


def parquet_market_dir(cache_dir: Path, market: str) -> Path:
    """Directory holding all tickers for one market.  e.g. ``/cache/crypto``."""
    return cache_dir / market


def parquet_ticker_dir(cache_dir: Path, market: str, ticker: str) -> Path:
    """Directory holding all daily files for one ticker.
    e.g. ``/cache/crypto/KRW-BTC``."""
    return cache_dir / market / ticker
