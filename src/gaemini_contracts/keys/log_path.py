"""Log path helpers (B4).

Canonical layout: `{log_root}/{instance}/{strategy}/{date}.jsonl`.
Writer (gaemini-core StrategyLogger) and reader (gaemini-view logs view)
must agree.
"""
from __future__ import annotations

from datetime import date as Date
from pathlib import Path

from gaemini_contracts.naming.instance import validate_instance_name


def log_path(
    log_root: Path,
    instance: str,
    strategy: str,
    day: Date,
) -> Path:
    validate_instance_name(instance)
    return log_root / instance / strategy / f"{day.isoformat()}.jsonl"


def log_instance_dir(log_root: Path, instance: str) -> Path:
    validate_instance_name(instance)
    return log_root / instance


def log_strategy_dir(log_root: Path, instance: str, strategy: str) -> Path:
    validate_instance_name(instance)
    return log_root / instance / strategy
