from gaemini_contracts.schema import (
    EVENT_JOIN_KEY,
    EVENT_KINDS,
    EVENT_PARTITION_GRANULARITY,
    EVENT_PARTITION_KEY,
    EVENT_SCHEMA_VERSION,
    EVENT_SCHEMAS,
    EVENT_TIMESTAMP_FORMAT,
)
from gaemini_contracts.time import KST_TIMESTAMP_FORMAT


def test_event_kinds_are_singular() -> None:
    assert EVENT_KINDS == (
        "trade",
        "orderbook",
        "ticker",
        "funding",
        "open_interest",
    )


def test_schemas_cover_exactly_event_kinds() -> None:
    assert set(EVENT_SCHEMAS) == set(EVENT_KINDS)


def test_join_key_contract() -> None:
    assert EVENT_JOIN_KEY == ("exchange", "symbol", "exchange_timestamp")


def test_every_kind_carries_join_key_in_order() -> None:
    """계약 불변식: 모든 kind 의 columns 가 조인 키를 (순서대로) 포함."""
    for kind, schema in EVENT_SCHEMAS.items():
        head = schema.columns[: len(EVENT_JOIN_KEY)]
        # exchange, symbol, exchange_timestamp 가 선두 3 컬럼.
        assert head == EVENT_JOIN_KEY, kind


def test_no_legacy_market_or_source_symbol_columns() -> None:
    """확정안: market 컬럼 제거, source_symbol 은 계약 표면에서 제외."""
    for kind, schema in EVENT_SCHEMAS.items():
        assert "market" not in schema.columns, kind
        assert "source_symbol" not in schema.columns, kind


def test_partition_key_is_kst_naive_timestamp() -> None:
    assert EVENT_PARTITION_KEY == "exchange_timestamp"
    assert EVENT_PARTITION_KEY in EVENT_JOIN_KEY
    assert EVENT_PARTITION_GRANULARITY == "day"
    assert EVENT_TIMESTAMP_FORMAT == KST_TIMESTAMP_FORMAT


def test_dtypes_reference_only_declared_columns() -> None:
    for kind, schema in EVENT_SCHEMAS.items():
        assert set(schema.dtypes) <= set(schema.columns), kind


def test_orderbook_has_15_nullable_int32_price_levels() -> None:
    ob = EVENT_SCHEMAS["orderbook"]
    for i in range(15):
        assert ob.dtypes[f"bid{i}_px"] == "Int32"  # nullable
        assert ob.dtypes[f"ask{i}_px"] == "Int32"
        assert ob.dtypes[f"bid{i}_sz"] == "float32"
        assert ob.dtypes[f"ask{i}_sz"] == "float32"
    assert ob.dtypes["depth"] == "Int32"


def test_trade_dtypes() -> None:
    tr = EVENT_SCHEMAS["trade"]
    assert tr.dtypes == {
        "trade_price": "int32",
        "trade_volume": "float32",
        "sequential_id": "int64",
    }


def test_schema_version_is_int() -> None:
    assert isinstance(EVENT_SCHEMA_VERSION, int)
