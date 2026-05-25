from datetime import date
from pathlib import Path

import pytest

from gaemini_contracts.keys import (
    EVENT_FRAGMENT_GLOB,
    InvalidEventKind,
    event_day_file,
    event_fragment_dir,
    event_partition_paths,
    event_symbol_dir,
    validate_event_kind,
)
from gaemini_contracts.naming import InvalidPathSegment
from gaemini_contracts.schema import EVENT_KINDS

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
    for kind in EVENT_KINDS:
        validate_event_kind(kind)  # no raise


def test_fragment_glob_is_stable() -> None:
    assert EVENT_FRAGMENT_GLOB == "part-*.parquet"


def test_event_paths_validate_segments() -> None:
    with pytest.raises(InvalidPathSegment):
        event_day_file(Path("/d"), "trade", "../upbit", "KRW-BTC", DAY)
    with pytest.raises(InvalidPathSegment):
        event_day_file(Path("/d"), "trade", "upbit", "KRW/BTC", DAY)


def test_event_partition_paths_prefers_compacted_day_file(tmp_path: Path) -> None:
    compacted = event_day_file(tmp_path, "trade", "upbit", "KRW-BTC", DAY)
    compacted.parent.mkdir(parents=True)
    compacted.write_text("compacted", encoding="utf-8")

    fragments = event_fragment_dir(tmp_path, "trade", "upbit", "KRW-BTC", DAY)
    fragments.mkdir()
    (fragments / "part-000.parquet").write_text("fragment", encoding="utf-8")

    assert event_partition_paths(tmp_path, "trade", "upbit", "KRW-BTC", DAY, DAY) == [
        compacted
    ]


def test_event_partition_paths_uses_sorted_fragments_without_compacted_file(
    tmp_path: Path,
) -> None:
    fragments = event_fragment_dir(tmp_path, "trade", "upbit", "KRW-BTC", DAY)
    fragments.mkdir(parents=True)
    second = fragments / "part-002.parquet"
    first = fragments / "part-001.parquet"
    ignored = fragments / "tmp.parquet"
    second.write_text("2", encoding="utf-8")
    first.write_text("1", encoding="utf-8")
    ignored.write_text("x", encoding="utf-8")

    assert event_partition_paths(tmp_path, "trade", "upbit", "KRW-BTC", DAY, DAY) == [
        first,
        second,
    ]


def test_event_partition_paths_discovers_available_days(tmp_path: Path) -> None:
    first_day = date(2026, 5, 17)
    second_day = date(2026, 5, 18)
    first = event_day_file(tmp_path, "trade", "upbit", "KRW-BTC", first_day)
    first.parent.mkdir(parents=True)
    first.write_text("1", encoding="utf-8")
    second_fragments = event_fragment_dir(
        tmp_path, "trade", "upbit", "KRW-BTC", second_day
    )
    second_fragments.mkdir()
    second = second_fragments / "part-001.parquet"
    second.write_text("2", encoding="utf-8")

    assert event_partition_paths(tmp_path, "trade", "upbit", "KRW-BTC") == [
        first,
        second,
    ]


def test_event_partition_paths_rejects_inverted_range() -> None:
    with pytest.raises(ValueError):
        event_partition_paths(
            Path("/d"),
            "trade",
            "upbit",
            "KRW-BTC",
            date(2026, 5, 18),
            date(2026, 5, 17),
        )
