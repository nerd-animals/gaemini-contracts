from datetime import date
from pathlib import Path

import pytest

from gaemini_contracts.keys import (
    EVENT_FRAGMENT_GLOB,
    InvalidEventKind,
    event_day_file,
    event_fragment_dir,
    event_symbol_dir,
    validate_event_kind,
)

DAY = date(2026, 5, 17)


def test_event_day_file() -> None:
    p = event_day_file(Path("/data"), "trade", "upbit", "KRW-BTC", DAY)
    assert p == Path("/data/trade/upbit/KRW-BTC/2026-05-17.parquet")


def test_event_fragment_dir() -> None:
    d = event_fragment_dir(Path("/data"), "orderbook", "upbit", "KRW-BTC", DAY)
    assert d == Path("/data/orderbook/upbit/KRW-BTC/2026-05-17")


def test_event_symbol_dir() -> None:
    d = event_symbol_dir(Path("/data"), "funding", "binance", "BTCUSDT")
    assert d == Path("/data/funding/binance/BTCUSDT")


def test_fragment_dir_is_under_symbol_dir() -> None:
    """조각 디렉터리와 일 완본은 같은 symbol 디렉터리에 나란히 있다."""
    sym = event_symbol_dir(Path("/d"), "trade", "upbit", "KRW-BTC")
    frag = event_fragment_dir(Path("/d"), "trade", "upbit", "KRW-BTC", DAY)
    day_file = event_day_file(Path("/d"), "trade", "upbit", "KRW-BTC", DAY)
    assert frag.parent == sym
    assert day_file.parent == sym
    assert frag.name == day_file.stem  # "2026-05-17"


def test_unknown_kind_rejected() -> None:
    with pytest.raises(InvalidEventKind):
        event_day_file(Path("/d"), "trades", "upbit", "KRW-BTC", DAY)


def test_validate_event_kind_accepts_all_known() -> None:
    for kind in ("trade", "orderbook", "ticker", "funding", "open_interest"):
        validate_event_kind(kind)  # no raise


def test_fragment_glob_is_stable() -> None:
    assert EVENT_FRAGMENT_GLOB == "part-*.parquet"
