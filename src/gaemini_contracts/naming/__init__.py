"""Instance name validation.

An instance is one running gaemini-core process (e.g. ``paper-crypto``,
``live-crypto``). The name appears in Redis prefixes, log paths, and
dashboard URLs, so it must be filesystem- and URL-safe.

See :mod:`gaemini_contracts.naming.instance` for the rule and examples.
"""
from gaemini_contracts.naming.instance import (
    INSTANCE_NAME_PATTERN,
    InvalidInstanceName,
    validate_instance_name,
)

__all__ = [
    "INSTANCE_NAME_PATTERN",
    "InvalidInstanceName",
    "validate_instance_name",
]
