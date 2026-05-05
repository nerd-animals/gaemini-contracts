"""Schema version boundary validators (B6).

Every persisted JSON record carries ``schema_version: int`` at the top
level. Readers check it on the boundary and fail fast on mismatch — silent
corruption is more dangerous than a loud failure.

See :mod:`gaemini_contracts.versioning.validators` for the helpers.
"""
from gaemini_contracts.versioning.validators import (
    SchemaIncompatible,
    dump_versioned_json,
    parse_versioned_json,
)

__all__ = [
    "SchemaIncompatible",
    "dump_versioned_json",
    "parse_versioned_json",
]
