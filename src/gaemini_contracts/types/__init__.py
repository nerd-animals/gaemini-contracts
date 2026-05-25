"""Cross-repo 영속/캐시 레코드 스키마.

각 레코드는 최상단에 ``schema_version``을 들고 다니며 producer/consumer
contracts 버전이 다르면 fail-fast 로 거부된다.

커버 범위
    LogRecord          — 애플리케이션 로그        (core 가 쓰고 view 가 읽음, JSONL).
    TradeRecord        — 거래 체결 이벤트        (core 가 쓰고 view 가 읽음, JSONL).
    CommandRecord      — 명령 audit 이벤트       (core 가 쓰고 view 가 읽음, JSONL).
    OrderBookSnapshot  — 호가창 in-memory state  (data 가 쓰고 core/view 가 읽음, Redis).
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
