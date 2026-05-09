"""OrderBookSnapshot 의 형태와 값 invariants 를 고정한다.

JSONL 이 아니라 Redis 에 msgpack 으로 저장되는 in-memory state cache 라
parse_versioned_json 같은 helper 가 끼지 않는다 — 그래서 versioning helper
대신 직접 dict 비교로 검증한다.
"""
from __future__ import annotations

from gaemini_contracts.types import (
    ORDER_BOOK_SNAPSHOT_VERSION,
    OrderBookLevel,
    OrderBookSnapshot,
)


def _sample_snapshot(
    *,
    has_gap: bool = False,
    previous_received_at: str | None = None,
) -> OrderBookSnapshot:
    return OrderBookSnapshot(
        schema_version=ORDER_BOOK_SNAPSHOT_VERSION,
        exchange="upbit",
        market="KRW-BTC",
        exchange_timestamp="2026-05-09 11:30:42.123",
        received_at="2026-05-09 11:30:42.198",
        depth=2,
        bids=[
            OrderBookLevel(price=50_000_000.0, size=0.123),
            OrderBookLevel(price=49_999_000.0, size=0.456),
        ],
        asks=[
            OrderBookLevel(price=50_010_000.0, size=0.234),
            OrderBookLevel(price=50_011_000.0, size=0.789),
        ],
        has_gap=has_gap,
        previous_received_at=previous_received_at,
    )


def test_snapshot_version_constant() -> None:
    assert ORDER_BOOK_SNAPSHOT_VERSION == 1


def test_snapshot_carries_schema_version() -> None:
    snap = _sample_snapshot()
    assert snap["schema_version"] == ORDER_BOOK_SNAPSHOT_VERSION


def test_snapshot_required_fields() -> None:
    """필드 이름과 타입이 외부 contract 라 변경 시 schema_version bump 가 필요."""
    snap = _sample_snapshot()
    expected_keys = {
        "schema_version",
        "exchange",
        "market",
        "exchange_timestamp",
        "received_at",
        "depth",
        "bids",
        "asks",
        "has_gap",
        "previous_received_at",
    }
    assert set(snap.keys()) == expected_keys


def test_snapshot_has_gap_false_uses_none_previous() -> None:
    snap = _sample_snapshot(has_gap=False, previous_received_at=None)
    assert snap["has_gap"] is False
    assert snap["previous_received_at"] is None


def test_snapshot_has_gap_true_carries_previous_received_at() -> None:
    snap = _sample_snapshot(
        has_gap=True,
        previous_received_at="2026-05-09 11:30:30.000",
    )
    assert snap["has_gap"] is True
    assert snap["previous_received_at"] == "2026-05-09 11:30:30.000"


def test_orderbook_level_fields() -> None:
    level = OrderBookLevel(price=50_000_000.0, size=0.123)
    assert set(level.keys()) == {"price", "size"}
    assert level["price"] == 50_000_000.0
    assert level["size"] == 0.123


def test_top_level_export() -> None:
    """gaemini_contracts top-level 에서도 import 가능해야 한다."""
    from gaemini_contracts import (
        ORDER_BOOK_SNAPSHOT_VERSION as v,
    )
    from gaemini_contracts import (
        OrderBookLevel as L,
    )
    from gaemini_contracts import (
        OrderBookSnapshot as S,
    )

    assert v == 1
    assert L is OrderBookLevel
    assert S is OrderBookSnapshot
