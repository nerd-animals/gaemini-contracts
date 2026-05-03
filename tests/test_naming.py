import pytest

from gaemini_contracts.naming import (
    INSTANCE_NAME_PATTERN,
    InvalidInstanceName,
    validate_instance_name,
)


@pytest.mark.parametrize(
    "name",
    [
        "paper",
        "live",
        "paper-1",
        "paper-crypto-momentum",
        "live-crypto",
        "p12",
        "abc",
        "a-b-c-d-e",
    ],
)
def test_valid_names(name: str) -> None:
    validate_instance_name(name)


@pytest.mark.parametrize(
    "name",
    [
        "",
        "ab",  # too short (min 3)
        "Paper",  # uppercase not allowed
        "PAPER",
        "paper_1",  # underscore not allowed
        "1paper",  # must start with letter
        "-paper",  # must start with letter
        "paper.1",  # dot not allowed
        "paper:1",  # colon not allowed (would break Redis prefix parsing)
        "x" * 32,  # too long (max 31)
    ],
)
def test_invalid_names(name: str) -> None:
    with pytest.raises(InvalidInstanceName):
        validate_instance_name(name)


def test_non_string() -> None:
    with pytest.raises(InvalidInstanceName):
        validate_instance_name(123)  # type: ignore[arg-type]


def test_pattern_exposed() -> None:
    assert INSTANCE_NAME_PATTERN.fullmatch("paper-1")
    assert not INSTANCE_NAME_PATTERN.fullmatch("Paper")
