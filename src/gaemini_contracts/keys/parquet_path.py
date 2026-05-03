"""Parquet partition path helpers.

Canonical layout: `{cache_dir}/{market}/{ticker}/{date}.parquet`.
Writer (gaemini-data collector) and readers (gaemini-core, gaemini-view)
must agree on these paths.
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
    """Path to one (market, ticker, day) Parquet partition."""
    return cache_dir / market / ticker / f"{day.isoformat()}.parquet"


def parquet_market_dir(cache_dir: Path, market: str) -> Path:
    return cache_dir / market


def parquet_ticker_dir(cache_dir: Path, market: str, ticker: str) -> Path:
    return cache_dir / market / ticker
