"""Cross-repo 데이터 파일을 위한 경로 helper들.

쓰는 쪽(producer)과 읽는 쪽(consumer) 모두 이 helper를 호출하므로,
디스크 레이아웃이 코드 곳곳에 흩어진 f-string 으로 갈라지지 않는다.

커버 범위
    OHLCV Parquet     — ``parquet_path``, ``parquet_market_dir``, ``parquet_ticker_dir``
    이벤트 Parquet     — ``event_day_file``, ``event_partition_paths``
    애플리케이션 로그  — ``api_log_path``, ``system_log_path``, ``strategy_log_path``
    거래/명령 이력     — ``trade_log_path``, ``command_log_path``
"""
from gaemini_contracts.keys.command_log_path import (
    command_log_path,
    command_logs_dir,
)
from gaemini_contracts.keys.event_parquet_path import (
    EVENT_FRAGMENT_GLOB,
    InvalidEventKind,
    event_day_file,
    event_fragment_dir,
    event_partition_paths,
    event_symbol_dir,
    validate_event_kind,
)
from gaemini_contracts.keys.log_path import (
    api_log_path,
    log_instance_dir,
    log_path,
    log_strategy_dir,
    strategy_log_path,
    system_log_path,
)
from gaemini_contracts.keys.parquet_path import (
    parquet_market_dir,
    parquet_path,
    parquet_ticker_dir,
)
from gaemini_contracts.keys.trade_log_path import (
    trade_log_path,
    trades_dir,
)

__all__ = [
    "EVENT_FRAGMENT_GLOB",
    "InvalidEventKind",
    "api_log_path",
    "command_log_path",
    "command_logs_dir",
    "event_day_file",
    "event_fragment_dir",
    "event_partition_paths",
    "event_symbol_dir",
    "validate_event_kind",
    "log_path",
    "log_instance_dir",
    "log_strategy_dir",
    "strategy_log_path",
    "system_log_path",
    "parquet_path",
    "parquet_market_dir",
    "parquet_ticker_dir",
    "trade_log_path",
    "trades_dir",
]
