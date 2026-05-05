"""Trade log file path layout (TradeRecord JSONL).

Producer
    gaemini-core. Appends one line per trade fill event.

Consumer
    gaemini-view (trades view).

Canonical layout
    ``{log_root}/{instance}/{strategy}/trades/{date}.jsonl``

The trade log lives under each strategy's log directory in a dedicated
``trades/`` subfolder, so application logs and trade logs share the same
``{log_root}/{instance}/{strategy}/`` root and rotate by date.

Example
    >>> trade_log_path(Path("/var/log/gaemini"), "paper-crypto", "momentum",
    ...                date(2026, 5, 3))
    PosixPath('/var/log/gaemini/paper-crypto/momentum/trades/2026-05-03.jsonl')

This file is the source of truth for trade history (replaces the legacy
``AccountState.orders_history`` list).
"""
from __future__ import annotations

from datetime import date as Date
from pathlib import Path

from gaemini_contracts.naming.instance import validate_instance_name


def trade_log_path(
    log_root: Path,
    instance: str,
    strategy: str,
    day: Date,
) -> Path:
    """Path to the daily trade JSONL file for one (instance, strategy)."""
    validate_instance_name(instance)
    return log_root / instance / strategy / "trades" / f"{day.isoformat()}.jsonl"


def trades_dir(log_root: Path, instance: str, strategy: str) -> Path:
    """Directory holding all daily trade JSONL files for one strategy."""
    validate_instance_name(instance)
    return log_root / instance / strategy / "trades"
