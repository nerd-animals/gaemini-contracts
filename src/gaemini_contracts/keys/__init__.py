"""Cross-repo 데이터 파일을 위한 경로 helper들.

쓰는 쪽(producer)과 읽는 쪽(consumer) 모두 이 helper를 호출하므로,
디스크 레이아웃이 코드 곳곳에 흩어진 f-string 으로 갈라지지 않는다.

커버 범위
    OHLCV Parquet     — ``parquet_path``, ``parquet_market_dir``, ``parquet_ticker_dir``
    애플리케이션 로그  — ``log_path``, ``log_instance_dir``, ``log_strategy_dir``
    거래 이력         — ``trade_log_path``, ``trades_dir``
"""
from gaemini_contracts.keys.log_path import (
    log_instance_dir,
    log_path,
    log_strategy_dir,
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
    "log_path",
    "log_instance_dir",
    "log_strategy_dir",
    "parquet_path",
    "parquet_market_dir",
    "parquet_ticker_dir",
    "trade_log_path",
    "trades_dir",
]
