"""StrategyContext — per-strategy mutable state injected by the framework.

Loaded from Redis `{instance}:strategy:{name}:ctx`, passed into BaseStrategy.run,
saved back after each tick. Strategies treat ctx as immutable (return a new
dict via {**ctx, key: value}).

ADR-004 constraint: must be JSON-serializable (no numpy, datetime, etc.).
"""
from __future__ import annotations

from typing import Any

StrategyContext = dict[str, Any]
