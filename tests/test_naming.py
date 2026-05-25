import pytest

from gaemini_contracts.naming import (
    INSTANCE_NAME_PATTERN,
    STRATEGY_ID_PATTERN,
    InvalidInstanceName,
    InvalidPathSegment,
    InvalidStrategyId,
    validate_instance_name,
    validate_path_segment,
    validate_strategy_id,
)


@pytest.mark.parametrize(
    "name",
    [
        "paper",
        "live",
        "paper-1",
        "paper-crypto-momentum",
        "live-crypto",
        "p12",
        "abc",
        "a-b-c-d-e",
    ],
)
def test_valid_names(name: str) -> None:
    validate_instance_name(name)


@pytest.mark.parametrize(
    "name",
    [
        "",
        "ab",  # too short (min 3)
        "Paper",  # uppercase not allowed
        "PAPER",
        "paper_1",  # underscore not allowed
        "1paper",  # must start with letter
        "-paper",  # must start with letter
        "paper.1",  # dot not allowed
        "paper:1",  # colon not allowed (would break Redis prefix parsing)
        "x" * 32,  # too long (max 31)
    ],
)
def test_invalid_names(name: str) -> None:
    with pytest.raises(InvalidInstanceName):
        validate_instance_name(name)


def test_non_string() -> None:
    with pytest.raises(InvalidInstanceName):
        validate_instance_name(123)  # type: ignore[arg-type]


def test_pattern_exposed() -> None:
    assert INSTANCE_NAME_PATTERN.fullmatch("paper-1")
    assert not INSTANCE_NAME_PATTERN.fullmatch("Paper")


@pytest.mark.parametrize(
    "value",
    ["upbit", "KRW-BTC", "BTCUSDT", "005930", "fred:DGS10"],
)
def test_valid_path_segments(value: str) -> None:
    validate_path_segment(value, "symbol")


@pytest.mark.parametrize("value", ["", ".", "..", "KRW/BTC", "bad\0x", "bad\\x"])
def test_invalid_path_segments(value: str) -> None:
    with pytest.raises(InvalidPathSegment):
        validate_path_segment(value, "symbol")


@pytest.mark.parametrize("strategy_id", ["momentum", "momentum-1", "a"])
def test_valid_strategy_ids(strategy_id: str) -> None:
    validate_strategy_id(strategy_id)


@pytest.mark.parametrize("strategy_id", ["", "Momentum", "1momentum", "a_b", "../x"])
def test_invalid_strategy_ids(strategy_id: str) -> None:
    with pytest.raises(InvalidStrategyId):
        validate_strategy_id(strategy_id)


def test_strategy_pattern_exposed() -> None:
    assert STRATEGY_ID_PATTERN.fullmatch("momentum-1")
    assert not STRATEGY_ID_PATTERN.fullmatch("Momentum")
