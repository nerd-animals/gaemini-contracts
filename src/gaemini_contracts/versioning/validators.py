"""Schema version boundary validators (B6).

Every persisted JSON record (LogRecord, TradeRecord, …) carries
``schema_version: int`` at the top level. Readers check that field on the
boundary and fail fast on mismatch — *silent corruption is more dangerous
than a loud failure*.

Each concrete record type owns its own ``*_VERSION`` constant in its own
module and delegates serialization to the helpers below. This module is
intentionally type-agnostic so new record types can adopt versioning
without touching it.

Usage
    Read::

        line = file.readline().rstrip()
        record = parse_versioned_json(line, LOG_RECORD_VERSION, "LogRecord")
        # record is a dict; cast to the relevant TypedDict at the call site.

    Write::

        line = dump_versioned_json(dict(record), LOG_RECORD_VERSION, "LogRecord")
        file.write(line + "\\n")

When a reader sees ``SchemaIncompatible``
    Either bump ``gaemini-contracts`` in the consuming repo, or migrate the
    on-disk data to the current version. The exception message names which
    record type was mismatched and which versions were involved.
"""
from __future__ import annotations

import json
from typing import Any


class SchemaIncompatible(ValueError):
    """Raised when a payload's ``schema_version`` does not match the reader's
    expected version.

    Operator action: bump ``gaemini-contracts`` in this consumer, or run a
    migration on the data, or both.
    """


def parse_versioned_json(
    raw: str,
    expected_version: int,
    schema_name: str,
) -> dict[str, Any]:
    """Parse ``raw`` as JSON, ensure its top-level ``schema_version`` matches
    ``expected_version``, and return the resulting dict.

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
    """Verify ``payload['schema_version'] == expected_version``, then JSON-dump.

    Refuses to serialize a record whose schema_version is missing or wrong —
    that would silently produce an unreadable file.
    """
    actual = payload.get("schema_version")
    if actual != expected_version:
        raise SchemaIncompatible(
            f"{schema_name} dump expected schema_version={expected_version}, "
            f"got {actual!r}. Set the field before serializing."
        )
    return json.dumps(payload)
