"""LogRecord — 애플리케이션 로그 한 줄. JSONL 파일에 append-only로 쌓인다.

생산자 (Producer)
    gaemini-core (StrategyLogger). 로그 호출 한 번 = 한 줄.

소비자 (Consumer)
    gaemini-view (로그 화면). 한 줄씩 읽어 다음 함수로 파싱한다::

        parse_versioned_json(line, LOG_RECORD_VERSION, "LogRecord")

파일 경로 (``keys/log_path.py`` 참조)
    ``{log_root}/{instance}/{strategy}/{date}.jsonl``
    예) ``/var/log/gaemini/paper-crypto/momentum/2026-05-03.jsonl``

용어
    JSONL    : JSON Lines. 한 줄에 하나의 독립적인 JSON 객체가 담기는 포맷.
               파일 끝에 한 줄씩 덧붙이기만 하면 되어 스트리밍 로그에 적합.
    instance : 실행 중인 gaemini-core 프로세스 한 벌의 이름. 예) "paper-crypto".
    strategy : 그 instance 안에 등록된 전략의 이름. 예) "momentum".
    tick     : 전략을 한 번 실행하는 단위 사이클. 스케줄러가 주기적으로
               전략의 ``run()``을 호출할 때마다 1 tick.

예시 줄::

    {"schema_version": 2, "ts": "2026-05-03 17:01:30.000000",
     "level": "INFO", "source": "strategy", "tick_id": "t-42",
     "message": "ran momentum strategy",
     "extra": {"signals": 3, "elapsed_ms": 87}}
"""
from __future__ import annotations

from typing import Any, TypedDict

# LogRecord의 형태가 깨지는 변경(필드 이름 변경/제거, 타입 좁힘)이 있을 때마다
# 1씩 올린다. 읽는 쪽은 schema_version이 이 값과 다르면 줄을 거부한다.
#
# v2: ``ts`` 가 UTC ISO 8601 (``...+00:00``) → KST naive (``KST_TIMESTAMP_FORMAT``)
#     로 변경. contract 전체의 시간 표현을 KST 로 통일하기 위함이다 (자세한
#     배경은 :mod:`gaemini_contracts.time` 참조).
LOG_RECORD_VERSION = 2


class LogRecord(TypedDict):
    schema_version: int

    # 로그가 발생한 시각. KST naive, ``KST_TIMESTAMP_FORMAT`` 포맷의 문자열.
    # 예) "2026-05-03 17:01:30.000000"
    ts: str

    # 심각도. "DEBUG" / "INFO" / "WARNING" / "ERROR" 중 하나.
    level: str

    # 로그를 발생시킨 주체.
    #   "strategy" — 사용자 전략 코드(BaseStrategy.run 또는 hook)에서 발생.
    #   "system"   — 프레임워크/런타임 코드(스케줄러, broker 등)에서 발생.
    source: str

    # 이 로그가 속한 tick의 ID. tick 바깥에서 발생한 로그
    # (시작/종료, cron 레벨 이벤트 등)는 None.
    tick_id: str | None

    # 사람이 읽기 위한 메시지. 정형 데이터는 여기 말고 ``extra``에 둔다.
    message: str

    # 정형 key/value 쌍 (반드시 JSON 직렬화 가능). 필터링/대시보드 용도.
    # 큰 binary blob은 넣지 말 것 — 로그 파일이 비대해진다.
    # 예) {"strategy": "momentum", "signals": 3, "elapsed_ms": 87}
    extra: dict[str, Any]
