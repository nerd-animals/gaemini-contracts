"""LogRecord — 애플리케이션 로그 한 줄. JSONL 파일에 append-only로 쌓인다.

생산자 (Producer)
    gaemini-core (StrategyLogger). 로그 호출 한 번 = 한 줄.

소비자 (Consumer)
    gaemini-view (로그 화면). 한 줄씩 읽어 다음 함수로 파싱한다::

        parse_log_record(line)

파일 경로 (``keys/log_path.py`` 참조)
    API 로그      ``{log_root}/_api/logs/{date}.jsonl``
    system 로그   ``{log_root}/{instance}/logs/{date}.jsonl``
    strategy 로그 ``{log_root}/{instance}/{strategy}/logs/{date}.jsonl``

용어
    JSONL    : JSON Lines. 한 줄에 하나의 독립적인 JSON 객체가 담기는 포맷.
               파일 끝에 한 줄씩 덧붙이기만 하면 되어 스트리밍 로그에 적합.
    instance : 실행 중인 gaemini-core 프로세스 한 벌의 이름. 예) "paper-crypto".
    strategy : 그 instance 안에 등록된 전략의 이름. 예) "momentum".
    tick     : 전략을 한 번 실행하는 단위 사이클. 스케줄러가 주기적으로
               전략의 ``run()``을 호출할 때마다 1 tick.

예시 줄::

    {"schema_version": 3, "ts": "2026-05-03 17:01:30.000000",
     "level": "INFO", "source": "strategy:momentum", "tick_id": "t-42",
     "message": "ran momentum strategy",
     "extra": {"signals": 3, "elapsed_ms": 87}}
"""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Literal, NotRequired, Required, TypedDict, cast

from gaemini_contracts.types.json_value import JsonValue
from gaemini_contracts.versioning import (
    SchemaIncompatible,
    dump_versioned_json,
    parse_versioned_json,
)

# LogRecord의 형태가 깨지는 변경(필드 이름 변경/제거, 타입 좁힘)이 있을 때마다
# 1씩 올린다. 읽는 쪽은 schema_version이 이 값과 다르면 줄을 거부한다.
#
# v2: ``ts`` 가 UTC ISO 8601 (``...+00:00``) → KST naive (``KST_TIMESTAMP_FORMAT``)
#     로 변경. contract 전체의 시간 표현을 KST 로 통일하기 위함이다 (자세한
#     배경은 :mod:`gaemini_contracts.time` 참조).
# v3: core 내부 observability dataclass 와 분리된 view-facing 파일 포맷.
#     ``level`` 은 파일 경계에서 ``WARNING`` 으로 정규화하고, ``extra`` 는
#     JSON-safe 값만 허용한다.
LOG_RECORD_VERSION = 3


class LogRecord(TypedDict, total=False):
    schema_version: Required[int]

    # 로그가 발생한 시각. KST naive, ``KST_TIMESTAMP_FORMAT`` 포맷의 문자열.
    # 예) "2026-05-03 17:01:30.000000"
    ts: Required[str]

    # 심각도. "DEBUG" / "INFO" / "WARNING" / "ERROR" 중 하나.
    level: Required[Literal["DEBUG", "INFO", "WARNING", "ERROR"]]

    # 로그를 발생시킨 주체. 예) "api", "scheduler", "strategy:momentum".
    source: Required[str]

    # 사람이 읽기 위한 메시지. 정형 데이터는 여기 말고 ``extra``에 둔다.
    message: Required[str]

    # 정형 key/value 쌍 (반드시 JSON 직렬화 가능). 필터링/대시보드 용도.
    # 큰 binary blob은 넣지 말 것 — 로그 파일이 비대해진다.
    # 예) {"strategy": "momentum", "signals": 3, "elapsed_ms": 87}
    extra: Required[dict[str, JsonValue]]

    # 이 로그가 속한 tick의 ID. tick 바깥에서 발생한 로그
    # (시작/종료, cron 레벨 이벤트 등)는 None 이거나 생략된다.
    tick_id: NotRequired[str | None]


_REQUIRED_FIELDS: frozenset[str] = frozenset(
    {"schema_version", "ts", "level", "source", "message", "extra"}
)


def parse_log_record(raw: str) -> LogRecord:
    """LogRecord JSONL 한 줄을 파싱하고 version/required field 를 검증한다."""
    payload = parse_versioned_json(raw, LOG_RECORD_VERSION, "LogRecord")
    _validate_required_fields(payload, "LogRecord")
    return cast(LogRecord, payload)


def dump_log_record(record: LogRecord) -> str:
    """LogRecord 를 JSONL 한 줄 문자열로 직렬화한다."""
    payload = cast(dict[str, Any], dict(record))
    _validate_required_fields(payload, "LogRecord")
    return dump_versioned_json(payload, LOG_RECORD_VERSION, "LogRecord")


def _validate_required_fields(payload: Mapping[str, Any], schema_name: str) -> None:
    missing = sorted(_REQUIRED_FIELDS - payload.keys())
    if missing:
        raise SchemaIncompatible(
            f"{schema_name} missing required field(s): {', '.join(missing)}"
        )
