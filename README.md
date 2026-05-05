# gaemini-contracts

Cross-repo file-format and path contracts shared by `gaemini-data`,
`gaemini-core`, and `gaemini-view`.

The package owns the **append-only file boundaries** between repos:

- OHLCV Parquet column layout and KST partition policy
- Application log (`LogRecord`) JSONL format and path
- Trade log (`TradeRecord`) JSONL format and path
- Instance name validation
- Schema-version fail-fast on JSON record boundaries

It has **no runtime dependencies** (no `pandas`, no `redis`).

Mutable live state (`AccountState`, `StrategySpec`, etc.) is owned by
`gaemini-core` and exposed to view via Core's HTTP API. Such state is
intentionally **not** part of this package.

Every module's docstring is self-contained — open `src/` for the full
semantics, including domain-term definitions.

## Install

Pin to a tag in your consumer's `pyproject.toml`:

```toml
[project]
dependencies = [
    "gaemini-contracts @ git+https://github.com/nerd-animals/gaemini-contracts.git@v0.2.0",
]
```

Bumping the pin is a deliberate cross-repo migration step — see
[Versioning](#versioning) below.

## Usage

The surface comes in three flavours: **path helpers**, **validation**,
and **schema-version helpers**. All three appear in the examples below.

### `gaemini-data` — writing OHLCV Parquet

```python
from datetime import date
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

from gaemini_contracts.keys import parquet_path
from gaemini_contracts.schema import OHLCV_COLUMNS, MINUTE_SYMBOL_SUFFIX

def write_daily_bars(
    cache_dir: Path, market: str, ticker: str, day: date, table: pa.Table
) -> None:
    out = parquet_path(cache_dir, market, ticker, day)
    out.parent.mkdir(parents=True, exist_ok=True)
    # Enforce the canonical column order before writing.
    pq.write_table(table.select(list(OHLCV_COLUMNS)), out)

def write_minute_bars(
    cache_dir: Path, market: str, ticker: str, day: date, table: pa.Table
) -> None:
    # Minute bars live under a suffixed symbol so the (market, ticker, day)
    # path layout stays one-symbol-per-directory.
    write_daily_bars(cache_dir, market, ticker + MINUTE_SYMBOL_SUFFIX, day, table)
```

### `gaemini-core` — writing trade and application logs

```python
from datetime import date, datetime, timezone
from pathlib import Path

from gaemini_contracts.keys import log_path, trade_log_path
from gaemini_contracts.naming import validate_instance_name
from gaemini_contracts.types import (
    LOG_RECORD_VERSION, LogRecord,
    TRADE_RECORD_VERSION, TradeRecord,
)
from gaemini_contracts.versioning import dump_versioned_json

# Path helpers (log_path, trade_log_path, ...) validate the instance name
# internally, so a bad name can never produce a file path. Calling
# validate_instance_name once at config load is still useful: it fails
# fast at startup with a clear "your config is wrong" message, instead of
# crashing on the first log write much later.
def load_config(raw: dict) -> dict:
    validate_instance_name(raw["instance"])  # raises InvalidInstanceName on bad name
    return raw

def append_trade(
    log_root: Path, instance: str, strategy: str, trade: TradeRecord
) -> None:
    day = datetime.fromisoformat(trade["ts"]).astimezone(timezone.utc).date()
    path = trade_log_path(log_root, instance, strategy, day)
    path.parent.mkdir(parents=True, exist_ok=True)
    line = dump_versioned_json(dict(trade), TRADE_RECORD_VERSION, "TradeRecord")
    with path.open("a", encoding="utf-8") as f:
        f.write(line + "\n")

def append_log(
    log_root: Path, instance: str, strategy: str, record: LogRecord
) -> None:
    day = date.today()
    path = log_path(log_root, instance, strategy, day)
    path.parent.mkdir(parents=True, exist_ok=True)
    line = dump_versioned_json(dict(record), LOG_RECORD_VERSION, "LogRecord")
    with path.open("a", encoding="utf-8") as f:
        f.write(line + "\n")
```

### `gaemini-view` — reading trade logs

```python
from datetime import date
from pathlib import Path

from gaemini_contracts.keys import trade_log_path
from gaemini_contracts.types import TRADE_RECORD_VERSION, TradeRecord
from gaemini_contracts.versioning import parse_versioned_json, SchemaIncompatible

def load_trades(
    log_root: Path, instance: str, strategy: str, day: date
) -> list[TradeRecord]:
    path = trade_log_path(log_root, instance, strategy, day)
    if not path.exists():
        return []

    out: list[TradeRecord] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                record = parse_versioned_json(line, TRADE_RECORD_VERSION, "TradeRecord")
            except SchemaIncompatible:
                # Either bump gaemini-contracts in this consumer, or migrate the file.
                raise
            out.append(record)  # type: ignore[arg-type]
    return out
```

The same pattern applies to `LogRecord` (use `log_path` and
`LOG_RECORD_VERSION`) and to `OHLCV` Parquet (use `parquet_path` and
read with `pyarrow`).

## Versioning

Semantic. Breaking changes (renamed/removed field, narrowed type, changed
path layout) bump the major version; consumers must re-pin together.

Every JSONL record carries `schema_version: int` at the top level. The
per-record `*_VERSION` constants in this package are the canonical
expected values. Readers call `parse_versioned_json(line, EXPECTED_VERSION,
"RecordName")` and fail fast with `SchemaIncompatible` on mismatch —
silent corruption is more dangerous than a loud failure.

On `SchemaIncompatible` at runtime, the fix is to either bump the
`gaemini-contracts` pin in the consumer, or migrate the on-disk data.

## Layout

```
src/gaemini_contracts/
├── schema/      # OHLCV Parquet column schema + partition policy
├── keys/        # File path helpers (parquet, log, trade log)
├── types/       # JSONL record schemas (LogRecord, TradeRecord)
├── naming/      # Instance name validation
└── versioning/  # schema_version fail-fast helpers
```

Each module's docstring includes producer/consumer roles, the canonical
path or layout, term definitions, and a worked example. Read the source.
