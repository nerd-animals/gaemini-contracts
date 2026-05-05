"""Instance name validation (B1).

An *instance* is one running gaemini-core process — for example
``paper-crypto-momentum``, ``live-crypto``, ``paper-2``. The instance name
appears in:
    - Redis key prefixes  (``{instance}:strategy:{name}:...``)
    - Log directory paths (``{log_root}/{instance}/...``)
    - Dashboard URLs

So it must be filesystem- and URL-safe and must not collide with the colon
separator used in Redis prefixes.

Rule
    ``^[a-z][a-z0-9-]{2,30}$``
        - 3 to 31 chars total
        - starts with a letter
        - lowercase letters, digits, dashes only

Mode prefix (``paper-`` / ``live-``) is recommended but NOT enforced —
operators may want short names for one-off experiments.

Examples
    valid:    "paper", "live", "paper-1", "paper-crypto-momentum"
    invalid:  "Paper"     (uppercase)
              "1paper"    (leading digit)
              "paper_1"   (underscore not allowed)
              "paper:1"   (colon would break Redis prefix parsing)
              "ab"        (too short, min 3)
              "x" * 32    (too long, max 31)
"""
from __future__ import annotations

import re

INSTANCE_NAME_PATTERN: re.Pattern[str] = re.compile(r"^[a-z][a-z0-9-]{2,30}$")


class InvalidInstanceName(ValueError):
    """Raised when an instance name violates ``INSTANCE_NAME_PATTERN``."""


def validate_instance_name(name: str) -> None:
    """Raise ``InvalidInstanceName`` if the name does not match the rule.

    Called by every path/key helper that takes an ``instance`` argument, so
    a malformed instance name fails at construction time — before any file
    or Redis key is created.
    """
    if not isinstance(name, str):
        raise InvalidInstanceName(
            f"instance name must be str, got {type(name).__name__}"
        )
    if not INSTANCE_NAME_PATTERN.fullmatch(name):
        raise InvalidInstanceName(
            f"instance name {name!r} does not match {INSTANCE_NAME_PATTERN.pattern}"
        )
