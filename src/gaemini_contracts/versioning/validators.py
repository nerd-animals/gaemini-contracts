"""스키마 버전 경계 검증기.

영속화되는 모든 JSON 레코드(LogRecord, TradeRecord 등)는 최상단에
``schema_version: int`` 필드를 들고 다닌다. 읽는 쪽은 그 값이 자기가 아는
버전과 일치하는지 검사하고, 다르면 *바로 실패한다 (fail-fast)* —
*조용히 망가지는 것보다 시끄럽게 터지는 게 낫다.*

각 구체 레코드 타입은 자기 모듈에 ``*_VERSION`` 상수를 두고 아래 두 helper에
그 값을 넘긴다. 이 모듈은 어떤 타입에도 의존하지 않게 두어, 새 레코드 타입이
versioning을 도입할 때 이 모듈을 건드릴 필요가 없도록 했다.

용어
    fail-fast       : 잘못된 입력을 만나는 즉시 예외를 던져 멈추는 패턴.
                      늦게 터지면 데이터가 일관성 없는 상태로 더 진행되어
                      더 큰 사고로 이어진다.
    schema_version  : 레코드 형태(필드 이름, 타입)에 대한 정수 버전.
                      형태가 깨지는 변경이 생길 때마다 1씩 올린다.
    boundary        : 데이터가 프로세스/repo 경계를 넘어가는 지점.
                      파일 read/write가 대표적인 boundary.

사용
    읽기::

        line = file.readline().rstrip()
        record = parse_versioned_json(line, LOG_RECORD_VERSION, "LogRecord")
        # 반환은 dict — 호출 지점에서 해당 TypedDict로 cast해서 사용한다.

    쓰기::

        line = dump_versioned_json(dict(record), LOG_RECORD_VERSION, "LogRecord")
        file.write(line + "\\n")

``SchemaIncompatible``를 보면
    이 consumer의 ``gaemini-contracts``를 bump하거나, 디스크에 쌓인 데이터를
    현재 버전에 맞게 마이그레이션한다. 예외 메시지에 어느 레코드 타입이
    어떤 버전과 충돌했는지가 들어있다.
"""
from __future__ import annotations

import json
from typing import Any


class SchemaIncompatible(ValueError):
    """레코드의 ``schema_version``이 reader가 기대하는 버전과 다를 때 발생.

    조치: 이 consumer의 gaemini-contracts를 bump하거나 데이터를 마이그레이션한다.
    """


def parse_versioned_json(
    raw: str,
    expected_version: int,
    schema_name: str,
) -> dict[str, Any]:
    """``raw``를 JSON으로 파싱하고, 최상단 ``schema_version``이
    ``expected_version``과 같은지 확인한 뒤 dict로 반환한다.

    호출자가 결과 dict를 자기 TypedDict / dataclass로 cast해서 사용한다.
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
    """``payload['schema_version']``이 ``expected_version``과 같은지 확인하고
    JSON 문자열로 직렬화한다.

    schema_version이 없거나 다르면 직렬화를 거부한다 — 그대로 두면 읽을 수
    없는 파일이 조용히 만들어지기 때문이다.
    """
    actual = payload.get("schema_version")
    if actual != expected_version:
        raise SchemaIncompatible(
            f"{schema_name} dump expected schema_version={expected_version}, "
            f"got {actual!r}. Set the field before serializing."
        )
    return json.dumps(payload)
