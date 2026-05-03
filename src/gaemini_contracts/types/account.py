"""Account state — the persisted view of one strategy's holdings.

Stored as JSON under Redis key `{instance}:strategy:{name}:account`.
schema_version is required at the persistence boundary (B6).
"""
from __future__ import annotations

from typing import TypedDict

from gaemini_contracts.types.order import OrderResultData
from gaemini_contracts.versioning.validators import (
    dump_versioned_json,
    parse_versioned_json,
)

ACCOUNT_STATE_VERSION = 1


class PositionData(TypedDict):
    ticker: str
    qty: float
    avg_price: float
    current_price: float


class AccountState(TypedDict):
    schema_version: int
    name: str
    allocated_cash: float
    available_cash: float
    positions: dict[str, PositionData]
    orders_history: list[OrderResultData]
    total_fees: float
    return_rate: float


def parse_account_state(raw: str) -> AccountState:
    """Parse a JSON-encoded AccountState, fail-fast on schema_version mismatch."""
    payload = parse_versioned_json(raw, ACCOUNT_STATE_VERSION, "AccountState")
    return payload  # type: ignore[return-value]


def dump_account_state(state: AccountState) -> str:
    """Serialize an AccountState to JSON, ensuring schema_version is correct."""
    return dump_versioned_json(dict(state), ACCOUNT_STATE_VERSION, "AccountState")
