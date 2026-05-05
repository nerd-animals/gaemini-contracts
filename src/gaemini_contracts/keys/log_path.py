"""Application log file path layout (LogRecord JSONL).

Producer
    gaemini-core (StrategyLogger). Appends one line per log call.

Consumer
    gaemini-view (logs view).

Canonical layout
    ``{log_root}/{instance}/{strategy}/{date}.jsonl``

Example
    >>> log_path(Path("/var/log/gaemini"), "paper-crypto", "momentum",
    ...          date(2026, 5, 3))
    PosixPath('/var/log/gaemini/paper-crypto/momentum/2026-05-03.jsonl')

``instance`` is validated against the rule in ``naming/instance.py`` —
malformed names raise ``InvalidInstanceName`` before any path is built.
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
    """Path to the daily JSONL log file for one (instance, strategy)."""
    validate_instance_name(instance)
    return log_root / instance / strategy / f"{day.isoformat()}.jsonl"


def log_instance_dir(log_root: Path, instance: str) -> Path:
    """Root directory for all strategies of one instance."""
    validate_instance_name(instance)
    return log_root / instance


def log_strategy_dir(log_root: Path, instance: str, strategy: str) -> Path:
    """Directory holding daily log files (and the ``trades/`` subdir) for
    one strategy."""
    validate_instance_name(instance)
    return log_root / instance / strategy
