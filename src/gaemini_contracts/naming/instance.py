"""Instance name validation (B1).

An instance is one running gaemini-core process — for example
`paper-crypto-momentum`, `live-crypto`, `paper-2`. The name shows up in
Redis prefixes, log paths, and dashboard URLs, so it must be filesystem-
and URL-safe.

Pattern: `^[a-z][a-z0-9-]{2,30}$`
- 3 to 31 chars total
- starts with a letter
- only lowercase letters, digits, dashes
- mode prefix (paper-/live-) is recommended but not enforced — operators
  may want short names for one-off experiments.
"""
from __future__ import annotations

import re

INSTANCE_NAME_PATTERN: re.Pattern[str] = re.compile(r"^[a-z][a-z0-9-]{2,30}$")


class InvalidInstanceName(ValueError):
    pass


def validate_instance_name(name: str) -> None:
    """Raise InvalidInstanceName if the name violates the regex."""
    if not isinstance(name, str):
        raise InvalidInstanceName(
            f"instance name must be str, got {type(name).__name__}"
        )
    if not INSTANCE_NAME_PATTERN.fullmatch(name):
        raise InvalidInstanceName(
            f"instance name {name!r} does not match {INSTANCE_NAME_PATTERN.pattern}"
        )
