"""TradeRecord — one trade fill event, JSONL append-only.

Producer
    gaemini-core. Appends one line each time the broker returns a fill
    result (or a final non-filled status such as "cancelled").

Consumer
    gaemini-view (trades view). Parses each line via
    ``parse_versioned_json(line, TRADE_RECORD_VERSION, "TradeRecord")``.

File path (see ``keys/trade_log_path.py``)
    ``{log_root}/{instance}/{strategy}/trades/{date}.jsonl``
    The path encodes ``(instance, strategy)`` — those fields are NOT in
    the record itself, to keep lines small.

Source of truth
    This file replaces the legacy ``AccountState.orders_history`` list.
    Trade history lives only here; the file is the truth source.

Write order (recommended)
    1. Append the TradeRecord line to the JSONL file.
    2. Update Redis ``AccountState`` (cash, positions).
    File first → if Redis update fails, the trade is still recoverable.

Example line::

    {"schema_version": 1, "ts": "2026-05-03T08:01:31+00:00",
     "order_id": "o-42", "ticker": "KRW-BTC", "side": "buy",
     "filled_amount": 0.01, "filled_price": 50000000.0,
     "fee": 25.0, "status": "filled"}
"""
from __future__ import annotations

from typing import Literal, TypedDict

# Bump on any breaking change to TradeRecord (renamed / removed field,
# narrowed type). Readers reject lines whose schema_version does not match.
TRADE_RECORD_VERSION = 1


class TradeRecord(TypedDict):
    schema_version: int

    # UTC timestamp of the broker's response. ISO 8601.
    # e.g. "2026-05-03T08:01:31+00:00"
    ts: str

    # Broker-issued order ID. Unique within the broker; opaque to us.
    order_id: str

    # Trading pair / instrument symbol. Format follows the market.
    #   crypto: "KRW-BTC", "USDT-ETH"
    #   KRX:    "005930"
    ticker: str

    # Trade direction. ("hold" is a strategy-level concept and never appears
    # in a trade record — only filled or attempted orders are logged.)
    side: Literal["buy", "sell"]

    # Amount filled in this event, in BASE-asset units (not cash).
    # Always >= 0. For partial fills, carries only the chunk that filled now;
    # the remainder may produce additional TradeRecords or a "cancelled" one.
    filled_amount: float

    # Average fill price per base-asset unit, in QUOTE-asset units.
    # 0.0 when status is "failed" or "cancelled" (no fill happened).
    filled_price: float

    # Fee paid to the broker for this fill event, in QUOTE-asset units.
    fee: float

    # Outcome of this event. One TradeRecord = one event, not one order's
    # whole lifetime — a partially-filled-then-cancelled order produces
    # two records (a "partial" then a "cancelled").
    #   "filled"    — fully filled by this event.
    #   "partial"   — partial fill; more events may follow.
    #   "failed"    — broker rejected (insufficient balance, invalid order, …).
    #   "cancelled" — cancelled before any further fill.
    status: Literal["filled", "partial", "failed", "cancelled"]
