from gaemini_contracts.schema import (
    MINUTE_SYMBOL_SUFFIX,
    OHLCV_COLUMNS,
    PARTITION_GRANULARITY,
    PARTITION_TIMEZONE,
)


def test_ohlcv_columns_order() -> None:
    assert OHLCV_COLUMNS == ("date", "open", "high", "low", "close", "volume")


def test_partition_constants() -> None:
    assert PARTITION_TIMEZONE == "Asia/Seoul"
    assert PARTITION_GRANULARITY == "day"
    assert MINUTE_SYMBOL_SUFFIX == "_1m"
