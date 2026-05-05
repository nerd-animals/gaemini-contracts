"""TradeRecord — one trade fill, JSONL append-only.

File path: `{log_root}/{instance}/{strategy}/trades/{date}.jsonl`
Each line carries schema_version (B6) — view fails fast on mismatch.
The file path encodes (instance, strategy), so the record itself does not.

Replaces the legacy `AccountState.orders_history` list — trade history is
now an append-only log, with the file as the source of truth.
"""
from __future__ import annotations

from typing import Literal, TypedDict

TRADE_RECORD_VERSION = 1


class TradeRecord(TypedDict):
    schema_version: int
    ts: str  # UTC ISO 8601
    order_id: str
    ticker: str
    side: Literal["buy", "sell"]
    filled_amount: float
    filled_price: float
    fee: float
    status: Literal["filled", "partial", "failed", "cancelled"]
