"""Strategy registration spec and runtime metadata — persisted in Redis.

`StrategySpec` is the immutable contract describing how a strategy was
registered (class path, schedule, account, etc.). `StrategyMeta` is the
mutable runtime stats (last_executed_at, fail_count, etc.).

Both carry schema_version at the persistence boundary (B6).

Stored under:
- `{instance}:strategy:{name}:spec`  → StrategySpec
- `{instance}:strategy:{name}:meta`  → StrategyMeta
"""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, fields
from typing import Any, Literal

from gaemini_contracts.versioning.validators import (
    dump_versioned_json,
    parse_versioned_json,
)

STRATEGY_SPEC_VERSION = 1
STRATEGY_META_VERSION = 1


@dataclass(frozen=True)
class StrategySpec:
    name: str
    class_path: str
    params: dict[str, Any]
    output_type: str  # "signal", "target_portfolio", etc.
    schedule: str  # cron expression
    data_config: dict[str, Any]
    account_id: str
    initial_cash: float
    on_data_ready: Literal["auto_start", "notify_only"] = "auto_start"
    trade_alerts: bool = True

    def to_json(self) -> str:
        payload = asdict(self)
        payload["schema_version"] = STRATEGY_SPEC_VERSION
        return json.dumps(payload)

    @classmethod
    def from_json(cls, raw: str) -> "StrategySpec":
        data = parse_versioned_json(raw, STRATEGY_SPEC_VERSION, "StrategySpec")
        valid = {f.name for f in fields(cls)}
        return cls(**{k: v for k, v in data.items() if k in valid})


@dataclass
class StrategyMeta:
    last_executed_at: str | None = None
    fail_count: int = 0
    last_error: str | None = None
    last_reported_at: str | None = None
    report_cron: str | None = None

    def to_json(self) -> str:
        payload: dict[str, Any] = {
            "schema_version": STRATEGY_META_VERSION,
            "last_executed_at": self.last_executed_at,
            "fail_count": self.fail_count,
            "last_error": self.last_error,
            "last_reported_at": self.last_reported_at,
            "report_cron": self.report_cron,
        }
        return dump_versioned_json(payload, STRATEGY_META_VERSION, "StrategyMeta")

    @classmethod
    def from_json(cls, raw: str) -> "StrategyMeta":
        data = parse_versioned_json(raw, STRATEGY_META_VERSION, "StrategyMeta")
        valid = {f.name for f in fields(cls)}
        return cls(**{k: v for k, v in data.items() if k in valid})
