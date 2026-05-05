"""Cross-repo 로그 파일의 JSONL 레코드 스키마.

각 레코드는 최상단에 ``schema_version``을 들고 다니며,
:func:`gaemini_contracts.versioning.parse_versioned_json` 으로 읽을 때
버전이 다르면 fail-fast 로 거부된다.

커버 범위
    LogRecord    — 애플리케이션 로그   (core가 쓰고 view가 읽음).
    TradeRecord  — 거래 체결 이벤트   (core가 쓰고 view가 읽음).
"""
from gaemini_contracts.types.log_record import LOG_RECORD_VERSION, LogRecord
from gaemini_contracts.types.trade_record import TRADE_RECORD_VERSION, TradeRecord

__all__ = [
    "LOG_RECORD_VERSION",
    "LogRecord",
    "TRADE_RECORD_VERSION",
    "TradeRecord",
]
