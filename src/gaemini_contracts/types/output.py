"""Strategy output types (Strategy → Core).

Discriminated union via the `type` Literal field on each variant.
Dispatchers use `output["type"]` rather than isinstance (TypedDict
does not support runtime isinstance checks).
"""
from __future__ import annotations

from typing import Literal, TypedDict, Union


class SignalItem(TypedDict):
    ticker: str
    action: Literal["buy", "sell", "hold"]
    weight: float
    price: float | None
    reason: str


class SignalData(TypedDict):
    type: Literal["signal"]
    signals: list[SignalItem]


class TargetPortfolioData(TypedDict):
    type: Literal["target_portfolio"]
    weights: dict[str, float]  # ticker → target weight (0.0 ~ 1.0)


# --- MVP 이후 구현 (인터페이스만 정의) ---


class TargetDeltaData(TypedDict):
    type: Literal["target_delta"]
    deltas: dict[str, float]


class AlphaScoreData(TypedDict):
    type: Literal["alpha_score"]
    scores: dict[str, float]


class ForecastItemData(TypedDict):
    expected_return: float
    confidence: float


class ForecastData(TypedDict):
    type: Literal["forecast"]
    forecasts: dict[str, ForecastItemData]


OutputType = Union[
    SignalData,
    TargetPortfolioData,
    TargetDeltaData,
    AlphaScoreData,
    ForecastData,
]

OUTPUT_TYPE_NAMES = Literal[
    "signal",
    "target_portfolio",
    "target_delta",
    "alpha_score",
    "forecast",
]
