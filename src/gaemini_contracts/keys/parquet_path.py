"""OHLCV Parquet 파일의 경로 레이아웃.

생산자 (Producer)
    gaemini-data. (시장, 종목, 날짜) 한 조합당 Parquet 파일 한 개를 쓴다.

소비자 (Consumer)
    gaemini-core  — 전략 데이터 로더.
    gaemini-view  — 차트 렌더링.

표준 레이아웃
    ``{cache_dir}/{market}/{ticker}/{date}.parquet``

예시
    >>> parquet_path(Path("/cache"), "crypto", "KRW-BTC", date(2026, 5, 3))
    PosixPath('/cache/crypto/KRW-BTC/2026-05-03.parquet')

``cache_dir``는 호출자가 (보통 환경변수에서 받아) 넘겨준다. 이 모듈은
``{market}/{ticker}/{date}.parquet`` 부분만 책임진다.

용어
    market : 시장 식별자.    예) "crypto", "krx".
    ticker : 종목 식별자.    예) crypto면 "KRW-BTC", KRX면 "005930".
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
    """(market, ticker, day) 조합 한 건의 Parquet 파일 경로."""
    return cache_dir / market / ticker / f"{day.isoformat()}.parquet"


def parquet_market_dir(cache_dir: Path, market: str) -> Path:
    """한 시장의 모든 종목이 모이는 디렉토리. 예) ``/cache/crypto``."""
    return cache_dir / market


def parquet_ticker_dir(cache_dir: Path, market: str, ticker: str) -> Path:
    """한 종목의 모든 일자별 파일이 모이는 디렉토리.
    예) ``/cache/crypto/KRW-BTC``."""
    return cache_dir / market / ticker
