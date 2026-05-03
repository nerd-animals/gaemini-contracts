"""Round-trip serialization for persisted TypedDict / dataclass types.

Each persisted type must:
1. include schema_version on dump
2. fail-fast on parse if schema_version is missing or wrong
"""
import json

import pytest

from gaemini_contracts.types.account import (
    ACCOUNT_STATE_VERSION,
    AccountState,
    dump_account_state,
    parse_account_state,
)
from gaemini_contracts.types.spec import (
    STRATEGY_META_VERSION,
    STRATEGY_SPEC_VERSION,
    StrategyMeta,
    StrategySpec,
)
from gaemini_contracts.versioning import SchemaIncompatible


# -- AccountState ----------------------------------------------------------


def _sample_account_state() -> AccountState:
    return AccountState(
        schema_version=ACCOUNT_STATE_VERSION,
        name="momentum",
        allocated_cash=1_000_000.0,
        available_cash=900_000.0,
        positions={},
        orders_history=[],
        total_fees=0.0,
        return_rate=0.0,
    )


def test_account_state_round_trip() -> None:
    state = _sample_account_state()
    raw = dump_account_state(state)
    parsed = parse_account_state(raw)
    assert parsed == state
    assert parsed["schema_version"] == ACCOUNT_STATE_VERSION


def test_account_state_dump_requires_version() -> None:
    bad = dict(_sample_account_state())
    bad.pop("schema_version")
    with pytest.raises(SchemaIncompatible):
        dump_account_state(bad)  # type: ignore[arg-type]


def test_account_state_parse_rejects_wrong_version() -> None:
    payload = dict(_sample_account_state())
    payload["schema_version"] = 999
    raw = json.dumps(payload)
    with pytest.raises(SchemaIncompatible):
        parse_account_state(raw)


# -- StrategySpec ----------------------------------------------------------


def _sample_spec() -> StrategySpec:
    return StrategySpec(
        name="momentum",
        class_path="strategies.momentum.MomentumStrategy",
        params={"window": 20},
        output_type="signal",
        schedule="*/1 * * * *",
        data_config={"market": "crypto", "tickers": ["BTC"]},
        account_id="default",
        initial_cash=1_000_000.0,
    )


def test_strategy_spec_round_trip() -> None:
    spec = _sample_spec()
    raw = spec.to_json()
    parsed = StrategySpec.from_json(raw)
    assert parsed == spec


def test_strategy_spec_json_includes_version() -> None:
    spec = _sample_spec()
    raw = spec.to_json()
    payload = json.loads(raw)
    assert payload["schema_version"] == STRATEGY_SPEC_VERSION


def test_strategy_spec_parse_rejects_wrong_version() -> None:
    spec = _sample_spec()
    payload = json.loads(spec.to_json())
    payload["schema_version"] = 999
    raw = json.dumps(payload)
    with pytest.raises(SchemaIncompatible):
        StrategySpec.from_json(raw)


def test_strategy_spec_extra_fields_ignored() -> None:
    spec = _sample_spec()
    payload = json.loads(spec.to_json())
    payload["future_field"] = "ignore-me"
    raw = json.dumps(payload)
    parsed = StrategySpec.from_json(raw)
    assert parsed == spec


# -- StrategyMeta ----------------------------------------------------------


def test_strategy_meta_default_round_trip() -> None:
    meta = StrategyMeta()
    raw = meta.to_json()
    parsed = StrategyMeta.from_json(raw)
    assert parsed == meta


def test_strategy_meta_with_values_round_trip() -> None:
    meta = StrategyMeta(
        last_executed_at="2026-05-03T08:00:00+00:00",
        fail_count=2,
        last_error="timeout",
        report_cron="0 9 * * *",
    )
    parsed = StrategyMeta.from_json(meta.to_json())
    assert parsed == meta


def test_strategy_meta_json_includes_version() -> None:
    payload = json.loads(StrategyMeta().to_json())
    assert payload["schema_version"] == STRATEGY_META_VERSION


def test_strategy_meta_parse_rejects_wrong_version() -> None:
    payload = json.loads(StrategyMeta().to_json())
    payload["schema_version"] = 999
    with pytest.raises(SchemaIncompatible):
        StrategyMeta.from_json(json.dumps(payload))
