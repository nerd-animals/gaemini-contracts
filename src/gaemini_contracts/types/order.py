"""Order types crossing the strategy ↔ broker boundary.

Both types are nested inside higher-level persisted records (AccountState
holds OrderResultData history; NetOrderData is in-process only). They
do not carry their own schema_version — versions are enforced at the
outermost persisted record.
"""
from __future__ import annotations

from typing import Literal, TypedDict


class OrderResultData(TypedDict):
    order_id: str
    ticker: str
    side: Literal["buy", "sell"]
    filled_amount: float
    filled_price: float
    fee: float
    status: Literal["filled", "partial", "failed", "cancelled"]
    ts: str  # UTC ISO 8601


class NetOrderData(TypedDict):
    ticker: str
    side: Literal["buy", "sell"]
    amount: float
    order_type: Literal["market", "limit"]
    price: float | None
    source_strategies: list[str]
