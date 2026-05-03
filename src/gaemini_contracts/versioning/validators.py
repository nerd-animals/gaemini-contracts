"""Generic boundary validator — version check + JSON parse.

Concrete persisted types (AccountState, StrategySpec, StrategyMeta, LogRecord)
define their own VERSION constant in their own module and delegate to the
helpers below. This keeps the validator module type-agnostic and avoids
circular imports.

B6: every cross-process boundary is fail-fast on schema_version mismatch.
Silent corruption is more dangerous than a loud failure.
"""
from __future__ import annotations

import json
from typing import Any


class SchemaIncompatible(ValueError):
    """Raised when a payload's schema_version does not match what the reader expects.

    Operator action: bump gaemini-contracts in the consuming repo, or run a
    migration on the data, or both.
    """


def parse_versioned_json(
    raw: str,
    expected_version: int,
    schema_name: str,
) -> dict[str, Any]:
    """Parse JSON, ensure top-level schema_version field matches, return dict.

    Concrete callers cast the returned dict to their TypedDict / dataclass.
    """
    payload = json.loads(raw)
    if not isinstance(payload, dict):
        raise SchemaIncompatible(
            f"{schema_name} payload is not a JSON object: {type(payload).__name__}"
        )
    actual = payload.get("schema_version")
    if actual != expected_version:
        raise SchemaIncompatible(
            f"{schema_name} schema_version mismatch: "
            f"got {actual!r}, expected {expected_version}. "
            "Bump gaemini-contracts in this consumer or migrate the data."
        )
    return payload


def dump_versioned_json(
    payload: dict[str, Any],
    expected_version: int,
    schema_name: str,
) -> str:
    """Ensure schema_version is correct, then JSON-dump."""
    actual = payload.get("schema_version")
    if actual != expected_version:
        raise SchemaIncompatible(
            f"{schema_name} dump expected schema_version={expected_version}, "
            f"got {actual!r}. Set the field before serializing."
        )
    return json.dumps(payload)
