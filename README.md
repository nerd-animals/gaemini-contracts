# gaemini-contracts

File-format and path contracts shared by `gaemini-data`, `gaemini-core`, and `gaemini-view`.

This package owns the **append-only file** boundaries between repos:

- OHLCV Parquet — columns, KST partition policy, path layout
- Application logs — `LogRecord` JSONL + path layout
- Trade logs — `TradeRecord` JSONL + path layout
- Instance name validation (B1)
- Schema version boundary validators (B6 fail-fast)

Mutable live state (`AccountState`, `StrategySpec`, `StrategyMeta`, etc.) is
owned by `gaemini-core` and exposed to `gaemini-view` via Core's HTTP API.
It is **not** a cross-repo contract.

## Architectural principles

- **누적 / append-only → 파일** (cross-repo via this package)
  - OHLCV (data writes, core/view read)
  - LogRecord (core writes, view reads)
  - TradeRecord (core writes, view reads)
- **최신 상태 / mutable snapshot → Core HTTP API**
  - View never touches Core's Redis directly.

No runtime dependencies (no `pandas`, no `redis`).

## Install (consumer)

```toml
[project]
dependencies = [
    "gaemini-contracts @ git+https://github.com/nerd-animals/gaemini-contracts.git@v0.2.0",
]
```

## Public API

```python
from gaemini_contracts import (
    LogRecord, LOG_RECORD_VERSION,
    TradeRecord, TRADE_RECORD_VERSION,
)
from gaemini_contracts.schema import (
    OHLCV_COLUMNS, PARTITION_TIMEZONE, PARTITION_GRANULARITY, MINUTE_SYMBOL_SUFFIX,
)
from gaemini_contracts.keys import (
    parquet_path, parquet_market_dir, parquet_ticker_dir,
    log_path, log_instance_dir, log_strategy_dir,
    trade_log_path, trades_dir,
)
from gaemini_contracts.naming import validate_instance_name, INSTANCE_NAME_PATTERN
from gaemini_contracts.versioning import (
    parse_versioned_json, dump_versioned_json, SchemaIncompatible,
)
```

## Versioning policy

Semantic. Breaking changes in a major bump. All consumers must bump together.

Every JSONL record carries a top-level `schema_version: int`. Readers check
it on the boundary and fail-fast on mismatch via `SchemaIncompatible`.
