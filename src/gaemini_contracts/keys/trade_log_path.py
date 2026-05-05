"""Trade log path helpers.

Canonical layout: `{log_root}/{instance}/{strategy}/trades/{date}.jsonl`.
Writer (gaemini-core trade logger) and reader (gaemini-view trades view)
must agree.
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
    validate_instance_name(instance)
    return log_root / instance / strategy / "trades" / f"{day.isoformat()}.jsonl"


def trades_dir(log_root: Path, instance: str, strategy: str) -> Path:
    validate_instance_name(instance)
    return log_root / instance / strategy / "trades"
