"""Round-trip serialization for cross-repo JSONL records.

Each record carries a top-level schema_version (B6) so readers can
fail-fast on mismatch via parse_versioned_json.
"""
import json
from typing import Any

import pytest

from gaemini_contracts.types import (
    LOG_RECORD_VERSION,
    TRADE_RECORD_VERSION,
    LogRecord,
    TradeRecord,
)
from gaemini_contracts.versioning import (
    SchemaIncompatible,
    dump_versioned_json,
    parse_versioned_json,
)

# -- LogRecord -------------------------------------------------------------


def _sample_log() -> LogRecord:
    return LogRecord(
        schema_version=LOG_RECORD_VERSION,
        ts="2026-05-03 17:00:00.000000",
        level="INFO",
        source="strategy",
        tick_id="t-1",
        message="hello",
        extra={"k": "v"},
    )


def test_log_record_round_trip() -> None:
    record = _sample_log()
    raw = dump_versioned_json(dict(record), LOG_RECORD_VERSION, "LogRecord")
    parsed: dict[str, Any] = parse_versioned_json(raw, LOG_RECORD_VERSION, "LogRecord")
    assert parsed == record


def test_log_record_rejects_wrong_version() -> None:
    bad = dict(_sample_log())
    bad["schema_version"] = 999
    raw = json.dumps(bad)
    with pytest.raises(SchemaIncompatible):
        parse_versioned_json(raw, LOG_RECORD_VERSION, "LogRecord")


# -- TradeRecord ------------------------------------------------------------


def _sample_trade() -> TradeRecord:
    return TradeRecord(
        schema_version=TRADE_RECORD_VERSION,
        ts="2026-05-03 17:00:00.000000",
        order_id="o-1",
        ticker="KRW-BTC",
        side="buy",
        filled_amount=0.01,
        filled_price=50_000_000.0,
        fee=25.0,
        status="filled",
    )


def test_trade_record_round_trip() -> None:
    trade = _sample_trade()
    raw = dump_versioned_json(dict(trade), TRADE_RECORD_VERSION, "TradeRecord")
    parsed: dict[str, Any] = parse_versioned_json(
        raw, TRADE_RECORD_VERSION, "TradeRecord"
    )
    assert parsed == trade


def test_trade_record_rejects_wrong_version() -> None:
    bad = dict(_sample_trade())
    bad["schema_version"] = 999
    raw = json.dumps(bad)
    with pytest.raises(SchemaIncompatible):
        parse_versioned_json(raw, TRADE_RECORD_VERSION, "TradeRecord")


def test_trade_record_dump_requires_version() -> None:
    bad = dict(_sample_trade())
    bad.pop("schema_version")
    with pytest.raises(SchemaIncompatible):
        dump_versioned_json(bad, TRADE_RECORD_VERSION, "TradeRecord")


def test_trade_record_jsonl_line_round_trip() -> None:
    """Multiple TradeRecords concatenated with newlines (= JSONL file)."""
    a = _sample_trade()
    b = dict(_sample_trade())
    b["order_id"] = "o-2"
    b["side"] = "sell"

    line_a = dump_versioned_json(dict(a), TRADE_RECORD_VERSION, "TradeRecord")
    line_b = dump_versioned_json(b, TRADE_RECORD_VERSION, "TradeRecord")
    file_content = line_a + "\n" + line_b

    parsed = [
        parse_versioned_json(line, TRADE_RECORD_VERSION, "TradeRecord")
        for line in file_content.splitlines()
    ]
    assert parsed[0]["order_id"] == "o-1"
    assert parsed[1]["order_id"] == "o-2"
    assert parsed[1]["side"] == "sell"
