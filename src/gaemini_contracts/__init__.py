"""Gaemini cross-repo 파일 경계 계약 패키지.

이 패키지는 ``gaemini-data``, ``gaemini-core``, ``gaemini-view`` 세 레포가
공유하는 *append-only 파일* 의 포맷과 경로만 보유한다.

가변 라이브 상태(``AccountState``, ``StrategySpec`` 등)는 ``gaemini-core``의
사적 영역이고, ``gaemini-view``에는 Core HTTP API로 노출된다 —
즉 그 부분은 더 이상 cross-repo 계약이 아니다.

각 하위 모듈 docstring을 보면 누가 쓰고(producer) 누가 읽는지(consumer),
파일 경로와 예시 줄까지 한 화면에 정리되어 있다.

용어
    cross-repo  : 여러 git repository가 공유하는 경계. 이 패키지의 존재 이유.
    append-only : 기존 줄을 수정하지 않고 끝에 한 줄씩 덧붙이기만 하는 방식.
                  파일을 시계열 로그처럼 다루는 데 적합.
"""

from gaemini_contracts.types.command_record import (
    COMMAND_RECORD_VERSION,
    CommandRecord,
    dump_command_record,
    parse_command_record,
)
from gaemini_contracts.types.json_value import JsonScalar, JsonValue
from gaemini_contracts.types.log_record import (
    LOG_RECORD_VERSION,
    LogRecord,
    dump_log_record,
    parse_log_record,
)
from gaemini_contracts.types.orderbook import (
    ORDER_BOOK_SNAPSHOT_VERSION,
    OrderBookLevel,
    OrderBookSnapshot,
    validate_orderbook_snapshot,
)
from gaemini_contracts.types.trade_record import (
    TRADE_RECORD_VERSION,
    TradeRecord,
    dump_trade_record,
    parse_trade_record,
)

__all__ = [
    "COMMAND_RECORD_VERSION",
    "CommandRecord",
    "JsonScalar",
    "JsonValue",
    "LOG_RECORD_VERSION",
    "LogRecord",
    "ORDER_BOOK_SNAPSHOT_VERSION",
    "OrderBookLevel",
    "OrderBookSnapshot",
    "TRADE_RECORD_VERSION",
    "TradeRecord",
    "dump_command_record",
    "dump_log_record",
    "dump_trade_record",
    "parse_command_record",
    "parse_log_record",
    "parse_trade_record",
    "validate_orderbook_snapshot",
]
