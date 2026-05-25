from datetime import date
from pathlib import Path

import pytest

from gaemini_contracts.keys import (
    api_log_path,
    command_log_path,
    command_logs_dir,
    log_instance_dir,
    log_strategy_dir,
    parquet_market_dir,
    parquet_path,
    parquet_ticker_dir,
    strategy_log_path,
    system_log_path,
    trade_log_path,
    trades_dir,
)
from gaemini_contracts.naming import (
    InvalidInstanceName,
    InvalidPathSegment,
    InvalidStrategyId,
)

# -- Parquet path -----------------------------------------------------------


def test_parquet_path() -> None:
    p = parquet_path(Path("/cache"), "crypto", "BTC", date(2026, 5, 3))
    assert p == Path("/cache/crypto/BTC/2026-05-03.parquet")


def test_parquet_dirs() -> None:
    assert parquet_market_dir(Path("/cache"), "krx") == Path("/cache/krx")
    assert parquet_ticker_dir(Path("/cache"), "krx", "005930") == Path(
        "/cache/krx/005930"
    )


def test_parquet_path_validates_segments() -> None:
    with pytest.raises(InvalidPathSegment):
        parquet_path(Path("/cache"), "../crypto", "BTC", date(2026, 5, 3))
    with pytest.raises(InvalidPathSegment):
        parquet_path(Path("/cache"), "crypto", "KRW/BTC", date(2026, 5, 3))


# -- Log path ---------------------------------------------------------------


def test_explicit_log_paths() -> None:
    root = Path("/var/log/gaemini")
    day = date(2026, 5, 3)

    assert api_log_path(root, day) == Path(
        "/var/log/gaemini/_api/logs/2026-05-03.jsonl"
    )
    assert system_log_path(root, "paper", day) == Path(
        "/var/log/gaemini/paper/logs/2026-05-03.jsonl"
    )
    assert strategy_log_path(root, "paper", "momentum", day) == Path(
        "/var/log/gaemini/paper/momentum/logs/2026-05-03.jsonl"
    )


def test_log_dirs() -> None:
    assert log_instance_dir(Path("/var/log/gaemini"), "paper") == Path(
        "/var/log/gaemini/paper"
    )
    assert log_strategy_dir(Path("/var/log/gaemini"), "paper", "momentum") == Path(
        "/var/log/gaemini/paper/momentum"
    )


def test_explicit_log_paths_validate_instance() -> None:
    with pytest.raises(InvalidInstanceName):
        system_log_path(Path("/var/log"), "Bad", date(2026, 5, 3))
    with pytest.raises(InvalidInstanceName):
        strategy_log_path(Path("/var/log"), "Bad", "x", date(2026, 5, 3))


def test_strategy_log_path_validates_strategy() -> None:
    with pytest.raises(InvalidStrategyId):
        strategy_log_path(Path("/var/log"), "paper", "../x", date(2026, 5, 3))


# -- Command log path -------------------------------------------------------


def test_command_log_path() -> None:
    p = command_log_path(Path("/var/log/gaemini"), "paper", date(2026, 5, 3))
    assert p == Path("/var/log/gaemini/paper/commands/2026-05-03.jsonl")


def test_command_logs_dir() -> None:
    assert command_logs_dir(Path("/var/log/gaemini"), "paper") == Path(
        "/var/log/gaemini/paper/commands"
    )


def test_command_log_path_validates_instance() -> None:
    with pytest.raises(InvalidInstanceName):
        command_log_path(Path("/var/log"), "Bad", date(2026, 5, 3))


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
