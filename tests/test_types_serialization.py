"""Round-trip serialization for cross-repo JSONL records.

Each record carries a top-level schema_version (B6) so readers can
fail-fast on mismatch via parse_versioned_json.
"""
import json

import pytest

from gaemini_contracts.types import (
    COMMAND_RECORD_VERSION,
    LOG_RECORD_VERSION,
    TRADE_RECORD_VERSION,
    CommandRecord,
    LogRecord,
    TradeRecord,
    dump_command_record,
    dump_log_record,
    dump_trade_record,
    parse_command_record,
    parse_log_record,
    parse_trade_record,
)
from gaemini_contracts.versioning import SchemaIncompatible

# -- LogRecord -------------------------------------------------------------


def _sample_log() -> LogRecord:
    return LogRecord(
        schema_version=LOG_RECORD_VERSION,
        ts="2026-05-03 17:00:00.000000",
        level="INFO",
        source="strategy:momentum",
        tick_id="t-1",
        message="hello",
        extra={"k": "v"},
    )


def test_log_record_round_trip() -> None:
    record = _sample_log()
    raw = dump_log_record(record)
    parsed = parse_log_record(raw)
    assert parsed == record


def test_log_record_rejects_wrong_version() -> None:
    bad = dict(_sample_log())
    bad["schema_version"] = 999
    raw = json.dumps(bad)
    with pytest.raises(SchemaIncompatible):
        parse_log_record(raw)


def test_log_record_rejects_missing_required_field() -> None:
    bad = dict(_sample_log())
    bad.pop("message")
    with pytest.raises(SchemaIncompatible):
        parse_log_record(json.dumps(bad))


# -- TradeRecord ------------------------------------------------------------


def _sample_trade() -> TradeRecord:
    return TradeRecord(
        schema_version=TRADE_RECORD_VERSION,
        ts="2026-05-03 17:00:00.000000",
        exchange="upbit",
        order_id="o-1",
        ticker="KRW-BTC",
        side="buy",
        filled_amount="0.01",
        filled_price="50000000",
        fee="25",
        fee_currency="KRW",
        status="filled",
        source="strategy",
    )


def test_trade_record_round_trip() -> None:
    trade = _sample_trade()
    raw = dump_trade_record(trade)
    parsed = parse_trade_record(raw)
    assert parsed == trade


def test_trade_record_rejects_wrong_version() -> None:
    bad = dict(_sample_trade())
    bad["schema_version"] = 999
    raw = json.dumps(bad)
    with pytest.raises(SchemaIncompatible):
        parse_trade_record(raw)


def test_trade_record_dump_requires_version() -> None:
    bad = dict(_sample_trade())
    bad.pop("schema_version")
    with pytest.raises(SchemaIncompatible):
        dump_trade_record(bad)  # type: ignore[arg-type]


def test_trade_record_rejects_missing_required_field() -> None:
    bad = dict(_sample_trade())
    bad.pop("filled_amount")
    with pytest.raises(SchemaIncompatible):
        parse_trade_record(json.dumps(bad))


def test_trade_record_jsonl_line_round_trip() -> None:
    """Multiple TradeRecords concatenated with newlines (= JSONL file)."""
    a = _sample_trade()
    b = dict(_sample_trade())
    b["order_id"] = "o-2"
    b["side"] = "sell"

    line_a = dump_trade_record(a)
    line_b = dump_trade_record(b)  # type: ignore[arg-type]
    file_content = line_a + "\n" + line_b

    parsed = [parse_trade_record(line) for line in file_content.splitlines()]
    assert parsed[0]["order_id"] == "o-1"
    assert parsed[1]["order_id"] == "o-2"
    assert parsed[1]["side"] == "sell"


# -- CommandRecord ----------------------------------------------------------


def _sample_command() -> CommandRecord:
    return CommandRecord(
        schema_version=COMMAND_RECORD_VERSION,
        ts="2026-05-03 17:00:00.000000",
        cmd_id="cmd-1",
        kind="deposit",
        requested_by="api",
        status="applied",
        payload={"currency": "KRW", "amount": "10000"},
        detail={"balance_after": "10000"},
    )


def test_command_record_round_trip() -> None:
    record = _sample_command()
    raw = dump_command_record(record)
    parsed = parse_command_record(raw)
    assert parsed == record


def test_command_record_rejects_wrong_version() -> None:
    bad = dict(_sample_command())
    bad["schema_version"] = 999
    with pytest.raises(SchemaIncompatible):
        parse_command_record(json.dumps(bad))


def test_command_record_rejects_missing_required_field() -> None:
    bad = dict(_sample_command())
    bad.pop("cmd_id")
    with pytest.raises(SchemaIncompatible):
        dump_command_record(bad)  # type: ignore[arg-type]
