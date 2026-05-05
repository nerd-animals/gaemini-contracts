from datetime import date
from pathlib import Path

import pytest

from gaemini_contracts.keys import (
    log_instance_dir,
    log_path,
    log_strategy_dir,
    parquet_market_dir,
    parquet_path,
    parquet_ticker_dir,
    trade_log_path,
    trades_dir,
)
from gaemini_contracts.naming import InvalidInstanceName


# -- Parquet path -----------------------------------------------------------


def test_parquet_path() -> None:
    p = parquet_path(Path("/cache"), "crypto", "BTC", date(2026, 5, 3))
    assert p == Path("/cache/crypto/BTC/2026-05-03.parquet")


def test_parquet_dirs() -> None:
    assert parquet_market_dir(Path("/cache"), "krx") == Path("/cache/krx")
    assert parquet_ticker_dir(Path("/cache"), "krx", "005930") == Path(
        "/cache/krx/005930"
    )


# -- Log path ---------------------------------------------------------------


def test_log_path() -> None:
    p = log_path(Path("/var/log/gaemini"), "paper", "momentum", date(2026, 5, 3))
    assert p == Path("/var/log/gaemini/paper/momentum/2026-05-03.jsonl")


def test_log_dirs() -> None:
    assert log_instance_dir(Path("/var/log/gaemini"), "paper") == Path(
        "/var/log/gaemini/paper"
    )
    assert log_strategy_dir(Path("/var/log/gaemini"), "paper", "momentum") == Path(
        "/var/log/gaemini/paper/momentum"
    )


def test_log_path_validates_instance() -> None:
    with pytest.raises(InvalidInstanceName):
        log_path(Path("/var/log"), "Bad", "x", date(2026, 5, 3))


# -- Trade log path ---------------------------------------------------------


def test_trade_log_path() -> None:
    p = trade_log_path(
        Path("/var/log/gaemini"), "paper", "momentum", date(2026, 5, 3)
    )
    assert p == Path("/var/log/gaemini/paper/momentum/trades/2026-05-03.jsonl")


def test_trades_dir() -> None:
    assert trades_dir(Path("/var/log/gaemini"), "paper", "momentum") == Path(
        "/var/log/gaemini/paper/momentum/trades"
    )


def test_trade_log_path_validates_instance() -> None:
    with pytest.raises(InvalidInstanceName):
        trade_log_path(Path("/var/log"), "Bad", "x", date(2026, 5, 3))


def test_trades_dir_validates_instance() -> None:
    with pytest.raises(InvalidInstanceName):
        trades_dir(Path("/var/log"), "Bad", "x")


def test_trade_log_lives_under_strategy_dir() -> None:
    """Trade log path must sit inside the strategy's log directory."""
    log = log_strategy_dir(Path("/r"), "paper", "momentum")
    trades = trades_dir(Path("/r"), "paper", "momentum")
    assert trades.parent == log
