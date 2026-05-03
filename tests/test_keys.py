from datetime import date
from pathlib import Path

import pytest

from gaemini_contracts.keys import (
    GLOBAL_MODE_KEY,
    account_last_error_key,
    account_snapshot_key,
    instance_prefix,
    log_instance_dir,
    log_path,
    log_strategy_dir,
    parquet_market_dir,
    parquet_path,
    parquet_ticker_dir,
    strategy_account_key,
    strategy_ctx_key,
    strategy_keys_pattern,
    strategy_meta_key,
    strategy_name_from_status_key,
    strategy_spec_key,
    strategy_status_key,
)
from gaemini_contracts.naming import InvalidInstanceName


# -- Redis keys -------------------------------------------------------------


def test_instance_prefix() -> None:
    assert instance_prefix("paper") == "paper:"
    assert instance_prefix("live-crypto") == "live-crypto:"


def test_instance_prefix_validates() -> None:
    with pytest.raises(InvalidInstanceName):
        instance_prefix("Paper")


def test_strategy_keys_consistent_format() -> None:
    inst, name = "paper", "momentum"
    assert strategy_account_key(inst, name) == "paper:strategy:momentum:account"
    assert strategy_ctx_key(inst, name) == "paper:strategy:momentum:ctx"
    assert strategy_spec_key(inst, name) == "paper:strategy:momentum:spec"
    assert strategy_status_key(inst, name) == "paper:strategy:momentum:status"
    assert strategy_meta_key(inst, name) == "paper:strategy:momentum:meta"


def test_keys_are_instance_disambiguated() -> None:
    """Same strategy name in different instances must produce different keys (B3)."""
    paper = strategy_account_key("paper", "momentum")
    live = strategy_account_key("live", "momentum")
    assert paper != live


def test_strategy_keys_pattern() -> None:
    assert strategy_keys_pattern("paper") == "paper:strategy:*:status"


def test_strategy_name_from_status_key_round_trip() -> None:
    key = strategy_status_key("paper", "momentum-v2")
    assert strategy_name_from_status_key(key, "paper") == "momentum-v2"


def test_strategy_name_extraction_rejects_wrong_instance() -> None:
    key = strategy_status_key("paper", "momentum")
    with pytest.raises(ValueError):
        strategy_name_from_status_key(key, "live")


def test_strategy_name_extraction_rejects_non_status_key() -> None:
    key = strategy_account_key("paper", "momentum")
    with pytest.raises(ValueError):
        strategy_name_from_status_key(key, "paper")


def test_account_keys() -> None:
    assert account_snapshot_key("live", "crypto-1") == "live:account:crypto-1:snapshot"
    assert (
        account_last_error_key("live", "crypto-1") == "live:account:crypto-1:last_error"
    )


def test_global_mode_key_no_prefix() -> None:
    """Global keys are not instance-prefixed."""
    assert GLOBAL_MODE_KEY == "gaemini:mode"


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
