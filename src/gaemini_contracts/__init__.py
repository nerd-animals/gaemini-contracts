"""Public contracts surface for Gaemini cross-process boundaries.

Re-exports the symbols consumers most commonly need. Sub-modules
(`types`, `protocols`, `keys`, etc.) provide the full API.
"""

from gaemini_contracts.strategy.base import BaseStrategy
from gaemini_contracts.types.account import AccountState, PositionData
from gaemini_contracts.types.context import StrategyContext
from gaemini_contracts.types.order import NetOrderData, OrderResultData
from gaemini_contracts.types.output import (
    OUTPUT_TYPE_NAMES,
    AlphaScoreData,
    ForecastData,
    ForecastItemData,
    OutputType,
    SignalData,
    SignalItem,
    TargetDeltaData,
    TargetPortfolioData,
)
from gaemini_contracts.types.spec import StrategyMeta, StrategySpec

__all__ = [
    "BaseStrategy",
    "AccountState",
    "PositionData",
    "StrategyContext",
    "NetOrderData",
    "OrderResultData",
    "OUTPUT_TYPE_NAMES",
    "AlphaScoreData",
    "ForecastData",
    "ForecastItemData",
    "OutputType",
    "SignalData",
    "SignalItem",
    "TargetDeltaData",
    "TargetPortfolioData",
    "StrategyMeta",
    "StrategySpec",
]
