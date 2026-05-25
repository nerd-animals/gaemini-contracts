"""CommandRecord — view-facing 명령 audit JSONL 레코드."""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Literal, NotRequired, Required, TypedDict, cast

from gaemini_contracts.versioning import (
    SchemaIncompatible,
    dump_versioned_json,
    parse_versioned_json,
)

COMMAND_RECORD_VERSION = 1


class CommandRecord(TypedDict, total=False):
    schema_version: Required[int]

    # 명령 요청/처리 시각. KST naive, ``KST_TIMESTAMP_FORMAT`` 포맷의 문자열.
    ts: Required[str]

    # command audit stream 안에서 식별 가능한 ID.
    cmd_id: Required[str]

    # view 가 funding/transfer 이력을 구분해서 렌더링하는 최소 종류.
    kind: Required[Literal["deposit", "refresh_balance", "transfer"]]

    # 명령 요청 주체. 예) "api", "operator:sangyuk", "system".
    requested_by: Required[str]

    # 명령 처리 상태.
    status: Required[Literal["pending", "applied", "failed"]]

    # 명령별 입력값. contracts 는 command 내부 schema 를 소유하지 않고 문자열
    # map 으로 audit 표면만 고정한다.
    payload: Required[dict[str, str]]

    # 적용 결과의 추가 정보.
    detail: NotRequired[dict[str, str]]

    # status="failed" 일 때 실패 이유.
    error: NotRequired[str]


_REQUIRED_FIELDS: frozenset[str] = frozenset(
    {
        "schema_version",
        "ts",
        "cmd_id",
        "kind",
        "requested_by",
        "status",
        "payload",
    }
)


def parse_command_record(raw: str) -> CommandRecord:
    """CommandRecord JSONL 한 줄을 파싱하고 version/required field 를 검증한다."""
    payload = parse_versioned_json(raw, COMMAND_RECORD_VERSION, "CommandRecord")
    _validate_required_fields(payload, "CommandRecord")
    return cast(CommandRecord, payload)


def dump_command_record(record: CommandRecord) -> str:
    """CommandRecord 를 JSONL 한 줄 문자열로 직렬화한다."""
    payload = cast(dict[str, Any], dict(record))
    _validate_required_fields(payload, "CommandRecord")
    return dump_versioned_json(payload, COMMAND_RECORD_VERSION, "CommandRecord")


def _validate_required_fields(payload: Mapping[str, Any], schema_name: str) -> None:
    missing = sorted(_REQUIRED_FIELDS - payload.keys())
    if missing:
        raise SchemaIncompatible(
            f"{schema_name} missing required field(s): {', '.join(missing)}"
        )
