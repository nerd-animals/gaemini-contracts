import json

import pytest

from gaemini_contracts.versioning import (
    SchemaIncompatible,
    dump_versioned_json,
    parse_versioned_json,
    validate_versioned_mapping,
)


def test_parse_round_trip() -> None:
    raw = json.dumps({"schema_version": 1, "x": 42})
    parsed = parse_versioned_json(raw, expected_version=1, schema_name="Foo")
    assert parsed == {"schema_version": 1, "x": 42}


def test_parse_rejects_wrong_version() -> None:
    raw = json.dumps({"schema_version": 2, "x": 42})
    with pytest.raises(SchemaIncompatible) as exc:
        parse_versioned_json(raw, expected_version=1, schema_name="Foo")
    assert "Foo" in str(exc.value)
    assert "got 2" in str(exc.value) or "got 2," in str(exc.value)
    assert "expected 1" in str(exc.value)


def test_parse_rejects_missing_version() -> None:
    raw = json.dumps({"x": 42})
    with pytest.raises(SchemaIncompatible):
        parse_versioned_json(raw, expected_version=1, schema_name="Foo")


def test_parse_rejects_non_object() -> None:
    raw = json.dumps([1, 2, 3])
    with pytest.raises(SchemaIncompatible):
        parse_versioned_json(raw, expected_version=1, schema_name="Foo")


def test_dump_round_trip() -> None:
    raw = dump_versioned_json(
        {"schema_version": 1, "x": 42}, expected_version=1, schema_name="Foo"
    )
    assert json.loads(raw) == {"schema_version": 1, "x": 42}


def test_dump_rejects_wrong_version() -> None:
    with pytest.raises(SchemaIncompatible):
        dump_versioned_json(
            {"schema_version": 2, "x": 42}, expected_version=1, schema_name="Foo"
        )


def test_dump_rejects_missing_version() -> None:
    with pytest.raises(SchemaIncompatible):
        dump_versioned_json({"x": 42}, expected_version=1, schema_name="Foo")


def test_validate_versioned_mapping_accepts_expected_version() -> None:
    validate_versioned_mapping(
        {"schema_version": 1, "x": 42},
        expected_version=1,
        schema_name="Foo",
    )


def test_validate_versioned_mapping_rejects_non_mapping() -> None:
    with pytest.raises(SchemaIncompatible):
        validate_versioned_mapping([1, 2, 3], expected_version=1, schema_name="Foo")


def test_validate_versioned_mapping_rejects_wrong_version() -> None:
    with pytest.raises(SchemaIncompatible):
        validate_versioned_mapping(
            {"schema_version": 2},
            expected_version=1,
            schema_name="Foo",
        )
