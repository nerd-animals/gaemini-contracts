# gaemini-contracts

Cross-process schema, key, and protocol contracts shared by `gaemini-data`, `gaemini-core`, and `gaemini-view`.

This package is the single source of truth for:

- TypedDict / dataclass schemas of every persisted payload (Redis values, JSONL records).
- Protocol definitions for cross-process boundaries (`OrderManagerProtocol`, `RedisProtocol`, `RealAccountProtocol`).
- Redis key formation helpers — instance-prefixed, `(instance, strategy)` tuple aware.
- Parquet path / column schema helpers.
- Instance name validation (B1 regex).
- Schema version constants and boundary validators (B6 fail-fast).

**No pandas dependency.** `DataBundle` and other pandas-bearing types live in `gaemini-core`. `BaseStrategy` references `DataBundle` via `TYPE_CHECKING` gate so runtime stays pandas-free.

## Install (consumer)

```toml
# consumer's pyproject.toml
[project]
dependencies = [
    "gaemini-contracts @ git+https://github.com/nerd-animals/gaemini-contracts.git@v0.1.0",
]
```

## Public API

```python
from gaemini_contracts import BaseStrategy
from gaemini_contracts.types import (
    AccountState, PositionData,
    OrderResultData, NetOrderData,
    OutputType, SignalData, TargetPortfolioData,
    StrategySpec, StrategyMeta,
)
from gaemini_contracts.protocols import (
    OrderManagerProtocol, RedisProtocol, RealAccountProtocol,
)
from gaemini_contracts.keys import (
    strategy_account_key, strategy_ctx_key, strategy_spec_key,
    strategy_status_key, strategy_meta_key,
    parquet_path, log_path,
)
from gaemini_contracts.naming import validate_instance_name
from gaemini_contracts.versioning import SchemaIncompatible
```

## Versioning policy

Semantic. Breaking changes in a major bump. All consumers must bump together — see ADR-021 in `gaemini-core/kb/adr.md`.

Every persisted Redis JSON / JSONL record carries a top-level `schema_version: int`. Readers check it on the boundary and fail-fast on mismatch.
