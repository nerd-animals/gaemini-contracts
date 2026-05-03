"""Redis key formation (B2 + B3).

Single source of truth for every key shape. Writers (gaemini-core) and
readers (gaemini-view) both call these helpers — no raw f-strings sprinkled
across the codebase.

Layout:
    {instance}:strategy:{name}:account
    {instance}:strategy:{name}:ctx
    {instance}:strategy:{name}:spec
    {instance}:strategy:{name}:status
    {instance}:strategy:{name}:meta
    {instance}:account:{account_id}:snapshot
    {instance}:account:{account_id}:last_error

Global keys (no instance prefix) live alongside instance-prefixed keys
in the same Redis DB. Currently used: gaemini:mode (legacy).
"""
from __future__ import annotations

from gaemini_contracts.naming.instance import validate_instance_name


def instance_prefix(instance: str) -> str:
    """Return the instance prefix segment, including trailing colon."""
    validate_instance_name(instance)
    return f"{instance}:"


# -- Strategy keys ----------------------------------------------------------


def strategy_account_key(instance: str, strategy: str) -> str:
    return f"{instance_prefix(instance)}strategy:{strategy}:account"


def strategy_ctx_key(instance: str, strategy: str) -> str:
    return f"{instance_prefix(instance)}strategy:{strategy}:ctx"


def strategy_spec_key(instance: str, strategy: str) -> str:
    return f"{instance_prefix(instance)}strategy:{strategy}:spec"


def strategy_status_key(instance: str, strategy: str) -> str:
    return f"{instance_prefix(instance)}strategy:{strategy}:status"


def strategy_meta_key(instance: str, strategy: str) -> str:
    return f"{instance_prefix(instance)}strategy:{strategy}:meta"


def strategy_keys_pattern(instance: str) -> str:
    """Pattern for SCAN/KEYS to find all strategy entries in this instance."""
    return f"{instance_prefix(instance)}strategy:*:status"


def strategy_name_from_status_key(key: str, instance: str) -> str:
    """Inverse of strategy_status_key — extract strategy name.

    Raises ValueError if the key is not a strategy status key for this instance.
    """
    prefix = instance_prefix(instance)
    expected_prefix = f"{prefix}strategy:"
    suffix = ":status"
    if not key.startswith(expected_prefix) or not key.endswith(suffix):
        raise ValueError(
            f"Not a strategy status key for instance {instance!r}: {key!r}"
        )
    return key[len(expected_prefix) : -len(suffix)]


# -- Account snapshot keys --------------------------------------------------


def account_snapshot_key(instance: str, account_id: str) -> str:
    return f"{instance_prefix(instance)}account:{account_id}:snapshot"


def account_last_error_key(instance: str, account_id: str) -> str:
    return f"{instance_prefix(instance)}account:{account_id}:last_error"


# -- Global keys (no instance prefix) ---------------------------------------

GLOBAL_MODE_KEY = "gaemini:mode"
"""Legacy single-mode key. With multi-instance, each instance has its own
mode in its instance config; this key may be deprecated."""
