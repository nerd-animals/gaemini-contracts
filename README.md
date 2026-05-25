# gaemini-contracts

Cross-repo file-format and path contracts shared by `gaemini-data`,
`gaemini-core`, and `gaemini-view`.

The package owns the **append-only file boundaries** between repos:

- OHLCV Parquet column layout and KST partition policy
- Application log (`LogRecord`) JSONL format and path
- Trade log (`TradeRecord`) JSONL format and path
- Command audit (`CommandRecord`) JSONL format and path
- Order book snapshot (`OrderBookSnapshot`) Redis msgpack layout
- Path-facing identifier validation
- Schema-version fail-fast on JSON and mapping boundaries

All time fields are **KST (Asia/Seoul) naive strings** — UTC↔KST conversion
happens once at the producer's entry point and never again. The canonical
formats live in `gaemini_contracts.time` (`KST_TIMESTAMP_FORMAT`,
`KST_DATE_FORMAT`, `KST_MINUTE_FORMAT`).

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
    "gaemini-contracts @ git+https://github.com/nerd-animals/gaemini-contracts.git@v0.8.0",
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
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from gaemini_contracts.keys import strategy_log_path, trade_log_path
from gaemini_contracts.naming import validate_instance_name
from gaemini_contracts.time import KST_TIMESTAMP_FORMAT, KST_TIMEZONE
from gaemini_contracts.types import (
    LogRecord, TradeRecord,
    dump_log_record, dump_trade_record,
)

# Path helpers validate instance/strategy/path segments internally, so a bad
# name can never produce a file path. Calling validate_instance_name once at
# config load is still useful: it fails fast at startup with a clear
# "your config is wrong" message, instead of crashing on the first log write.
def load_config(raw: dict) -> dict:
    validate_instance_name(raw["instance"])  # raises InvalidInstanceName on bad name
    return raw

def append_trade(
    log_root: Path, instance: str, strategy: str, trade: TradeRecord
) -> None:
    # ts is KST naive — the trading-day partition is just its date part.
    day = datetime.strptime(trade["ts"], KST_TIMESTAMP_FORMAT).date()
    path = trade_log_path(log_root, instance, strategy, day)
    path.parent.mkdir(parents=True, exist_ok=True)
    line = dump_trade_record(trade)
    with path.open("a", encoding="utf-8") as f:
        f.write(line + "\n")

def append_log(
    log_root: Path, instance: str, strategy: str, record: LogRecord
) -> None:
    day = datetime.now(ZoneInfo(KST_TIMEZONE)).date()
    path = strategy_log_path(log_root, instance, strategy, day)
    path.parent.mkdir(parents=True, exist_ok=True)
    line = dump_log_record(record)
    with path.open("a", encoding="utf-8") as f:
        f.write(line + "\n")
```

### `gaemini-view` — reading trade logs

```python
from datetime import date
from pathlib import Path

from gaemini_contracts.keys import trade_log_path
from gaemini_contracts.types import TradeRecord, parse_trade_record
from gaemini_contracts.versioning import SchemaIncompatible

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
                record = parse_trade_record(line)
            except SchemaIncompatible:
                # Either bump gaemini-contracts in this consumer, or migrate the file.
                raise
            out.append(record)  # type: ignore[arg-type]
    return out
```

The same pattern applies to `LogRecord` (use `strategy_log_path` and
`parse_log_record`), `CommandRecord` (use `command_log_path` and
`parse_command_record`), and to `OHLCV` Parquet (use `parquet_path` and
read with `pyarrow`).

## Versioning

This package follows semantic versioning, but the rules are tighter than
usual because every consumer must pin and re-pin in lockstep.

### Bump policy

**Patch** (`v0.2.0` → `v0.2.1`)
- Documentation, comments, examples.
- Internal refactors that do not change the public surface.
- Bug fixes that do not change observable behavior at the contract boundary.

**Minor** (`v0.2.0` → `v0.3.0`) — additive only, no consumer changes required
- New record type, new path helper, new constant.
- New *optional* field on an existing TypedDict (default-able, readers stay correct).
- Loosened validation (a previously-rejected input becomes accepted).

**Major** (`v0.2.0` → `v1.0.0`) — every consumer must update simultaneously
- Renamed or removed field on any record type.
- Type narrowed (e.g., `str` → `Literal[...]`).
- Changed path layout (any segment renamed, reordered, or added).
- Any `*_VERSION` constant incremented (record schema actually changed).
- Tightened validation (a previously-accepted input now rejected).

### Schema version (per record)

Every JSONL record carries `schema_version: int` at the top level. The
per-record `*_VERSION` constants in this package are the canonical
expected values. Readers call `parse_versioned_json(line, EXPECTED_VERSION,
"RecordName")` and fail fast with `SchemaIncompatible` on mismatch —
silent corruption is more dangerous than a loud failure.

On `SchemaIncompatible` at runtime, the fix is to either bump the
`gaemini-contracts` pin in the consumer, or migrate the on-disk data.

### Practical guidance

When extending a record type (e.g., adding a field to `TradeRecord`):
prefer making the new field optional with a sensible default. That keeps
the change *minor* — no `*_VERSION` bump, no consumer-side migration —
so the three repos can update on their own schedule.

Batch breaking changes. Group several breaking edits into one major bump
rather than spreading them across consecutive majors.

## Layout

```
src/gaemini_contracts/
├── schema/      # OHLCV Parquet column schema + partition policy
├── keys/        # File path helpers and event Parquet read planning
├── types/       # Record schemas for JSONL and Redis/msgpack boundaries
├── naming/      # Instance name and path segment validation
├── time.py      # KST timezone label + canonical time-string formats
└── versioning/  # schema_version fail-fast helpers
```

Each module's docstring includes producer/consumer roles, the canonical
path or layout, term definitions, and a worked example. Read the source.
