from __future__ import annotations

from typing import Protocol, runtime_checkable

from gaemini_contracts.types.order import NetOrderData, OrderResultData


@runtime_checkable
class OrderManagerProtocol(Protocol):
    async def execute(
        self, orders: list[NetOrderData]
    ) -> list[OrderResultData]: ...
