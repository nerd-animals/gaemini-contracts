from __future__ import annotations

from typing import Protocol, runtime_checkable

from gaemini_contracts.types.account import PositionData
from gaemini_contracts.types.order import NetOrderData, OrderResultData


@runtime_checkable
class RealAccountProtocol(Protocol):
    async def get_balance(self) -> float: ...
    async def get_positions(self) -> dict[str, PositionData]: ...
    async def place_order(self, order: NetOrderData) -> OrderResultData: ...
    async def get_current_price(self, ticker: str) -> float: ...
