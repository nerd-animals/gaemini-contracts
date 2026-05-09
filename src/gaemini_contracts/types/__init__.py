"""Cross-repo 영속/캐시 레코드 스키마.

각 레코드는 최상단에 ``schema_version``을 들고 다니며 producer/consumer
contracts 버전이 다르면 fail-fast 로 거부된다.

커버 범위
    LogRecord          — 애플리케이션 로그        (core 가 쓰고 view 가 읽음, JSONL).
    TradeRecord        — 거래 체결 이벤트        (core 가 쓰고 view 가 읽음, JSONL).
    OrderBookSnapshot  — 호가창 in-memory state  (data 가 쓰고 core/view 가 읽음, Redis).
"""
from gaemini_contracts.types.log_record import LOG_RECORD_VERSION, LogRecord
from gaemini_contracts.types.orderbook import (
    ORDER_BOOK_SNAPSHOT_VERSION,
    OrderBookLevel,
    OrderBookSnapshot,
)
from gaemini_contracts.types.trade_record import TRADE_RECORD_VERSION, TradeRecord

__all__ = [
    "LOG_RECORD_VERSION",
    "LogRecord",
    "ORDER_BOOK_SNAPSHOT_VERSION",
    "OrderBookLevel",
    "OrderBookSnapshot",
    "TRADE_RECORD_VERSION",
    "TradeRecord",
]
