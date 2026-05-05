"""스키마 버전 경계 검증기.

영속화되는 모든 JSON 레코드는 ``schema_version: int``를 최상단에 들고 다닌다.
읽는 쪽은 그 값이 자기가 기대하는 버전과 다르면 즉시 예외를 던진다 —
조용히 망가지는 것보다 시끄럽게 터지는 게 낫다.

helper 정의는 :mod:`gaemini_contracts.versioning.validators` 참조.
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
