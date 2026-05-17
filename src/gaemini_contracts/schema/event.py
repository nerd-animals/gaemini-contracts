"""이벤트 Parquet 스키마 — kind 별 컬럼·dtype·조인 키·파티션 정책.

OHLCV(:mod:`gaemini_contracts.schema.ohlcv`)와 별개인, 고빈도 이벤트 데이터
(체결·호가·티커·펀딩·미결제약정)의 디스크 포맷 단일 진실 공급원.

생산자 (Producer)
    gaemini-data. stream(Upbit ws) 또는 collector(Binance fapi)가
    :class:`EventParquetWriter` 로 append.

소비자 (Consumer)
    gaemini-core  — 전략 입력 / 백테스트.
    gaemini-view  — 차트·이력 렌더링.

용어
    kind   : 이벤트 종류. **이벤트 한 건의 이름 → 단수.** 예) "trade".
    exchange : 거래소 식별자. 소문자. 예) "upbit", "binance".
    symbol   : 거래소 원형 심볼. 예) "KRW-BTC"(upbit), "BTCUSDT"(binance).

설계 원칙 — 자리마다 내용물 그대로
    경로(:mod:`gaemini_contracts.keys.event_parquet_path`)의
    ``{kind}/{exchange}/{symbol}`` 세 자리 값은 각 row 의
    ``exchange`` / ``symbol`` 컬럼 값과 **글자까지 동일**하다.
    소비자는 별도 룩업 없이 경로만 보고 조인 키를 안다.

조인 키 계약 (invariant) — 전 kind 동일
    모든 kind 의 row 는 :data:`EVENT_JOIN_KEY` =
    ``("exchange", "symbol", "exchange_timestamp")`` 셋을 반드시 가진다.
    cross-repo 조인은 이 셋으로만 한다. (OHLCV 의 ``market``="crypto"(자산군)
    와 여기 ``exchange``="upbit"(거래소)는 *다른 것* 이라 다른 이름을 쓴다.)

시간 불변식
    전 kind ``exchange_timestamp`` 는 **KST naive 문자열**
    (``KST_TIMESTAMP_FORMAT`` = ``"YYYY-MM-DD HH:MM:SS.ffffff"``).
    Binance(UTC) 등 비-KST 소스는 producer 진입 시점에 KST 로 변환 완료된
    값만 컬럼에 들어간다 (자세한 배경은 :mod:`gaemini_contracts.time`).
    일 파티션 키(:data:`EVENT_PARTITION_KEY`)는 이 컬럼의 앞 10 글자.

dtype 캐스팅 계약
    writer 는 파일 간 dtype 흔들림을 막기 위해 write 직전 강제 캐스팅한다.
    호가 빈 레벨은 NA 가 될 수 있어 가격은 pandas **nullable ``Int32``**
    (대문자) — plain ``int32`` 는 NaN 캐스팅 불가. 이 NA 가능성이 계약의
    일부다 (소비자는 ``bidN_px``/``askN_px`` 가 null 일 수 있음을 가정).
"""
from __future__ import annotations

from dataclasses import dataclass

from gaemini_contracts.time import KST_TIMESTAMP_FORMAT

# 이벤트 스키마가 깨지는 변경(컬럼 이름 변경/제거, dtype 좁힘, 조인 키 변경)
# 마다 1씩 올린다. producer/consumer 의 contracts 버전이 다르면 디스크
# 레이아웃이 어긋나므로 pin 동시 갱신이 강제된다.
EVENT_SCHEMA_VERSION = 1

EVENT_KINDS: tuple[str, ...] = (
    "trade",
    "orderbook",
    "ticker",
    "funding",
    "open_interest",
)
"""허용되는 이벤트 kind. 전부 단수 (이벤트 한 건의 이름).

contracts 가 이 네임스페이스를 소유한다 — data 가 새 kind 를 적재하려면
먼저 여기에 추가(= 계약 변경)해야 소비자가 그 존재를 안다.
"""

EVENT_JOIN_KEY: tuple[str, ...] = ("exchange", "symbol", "exchange_timestamp")
"""전 kind 공통 cross-repo 조인 키. 이 셋 외의 식별 컬럼은 계약 표면에 없다."""

EVENT_PARTITION_KEY = "exchange_timestamp"
"""일 파티션 키. 이 컬럼(KST naive 문자열) 앞 10 글자가 ``YYYY-MM-DD`` 파티션."""

EVENT_PARTITION_GRANULARITY = "day"
"""(kind, exchange, symbol, KST 날짜) 조합마다 Parquet 일 1 파일."""

EVENT_TIMESTAMP_FORMAT = KST_TIMESTAMP_FORMAT
"""이벤트 전용 별칭 — :data:`gaemini_contracts.time.KST_TIMESTAMP_FORMAT` 와 동일."""


@dataclass(frozen=True)
class EventSchema:
    """한 kind 의 디스크 스키마. ``columns`` 순서가 표준 컬럼 순서다.

    ``dtypes`` 는 writer 가 강제 캐스팅하는 컬럼만 담는다 (문자열 컬럼 등
    캐스팅 불필요한 것은 생략 — 존재하는 컬럼만 캐스팅하는 writer 계약).
    """

    columns: tuple[str, ...]
    dtypes: dict[str, str]


_ORDERBOOK_DEPTH = 15
"""Upbit ws orderbook full-depth. 빈 레벨은 nullable ``Int32`` NA."""


def _orderbook_columns() -> tuple[str, ...]:
    cols = [
        "exchange",
        "symbol",
        "exchange_timestamp",
        "received_at",
        "has_gap",
        "depth",
    ]
    for i in range(_ORDERBOOK_DEPTH):
        cols += [f"bid{i}_px", f"bid{i}_sz", f"ask{i}_px", f"ask{i}_sz"]
    return tuple(cols)


def _orderbook_dtypes() -> dict[str, str]:
    dt: dict[str, str] = {"depth": "Int32"}
    for i in range(_ORDERBOOK_DEPTH):
        dt[f"bid{i}_px"] = "Int32"   # nullable — 빈 레벨 NA
        dt[f"bid{i}_sz"] = "float32"
        dt[f"ask{i}_px"] = "Int32"   # nullable — 빈 레벨 NA
        dt[f"ask{i}_sz"] = "float32"
    return dt


TRADE = EventSchema(
    columns=(
        "exchange",
        "symbol",
        "exchange_timestamp",
        "received_at",
        "trade_price",
        "trade_volume",
        "ask_bid",
        "sequential_id",
        "has_gap",
    ),
    dtypes={
        "trade_price": "int32",
        "trade_volume": "float32",
        "sequential_id": "int64",
    },
)
"""체결 틱. 생산자 stream(Upbit ws)."""

ORDERBOOK = EventSchema(
    columns=_orderbook_columns(),
    dtypes=_orderbook_dtypes(),
)
"""호가 시계열(full-depth 15, 1s 샘플). 생산자 stream(Upbit ws).

빈 레벨 ``bidN_px``/``askN_px`` 는 NA (nullable ``Int32``).
"""

TICKER = EventSchema(
    columns=(
        "exchange",
        "symbol",
        "exchange_timestamp",
        "received_at",
        "trade_price",
        "high_price",
        "low_price",
        "prev_closing_price",
        "signed_change_rate",
        "acc_trade_price_24h",
        "acc_trade_volume_24h",
        "highest_52_week_price",
        "lowest_52_week_price",
    ),
    dtypes={
        "trade_price": "int64",
        "high_price": "int64",
        "low_price": "int64",
        "prev_closing_price": "int64",
        "highest_52_week_price": "int64",
        "lowest_52_week_price": "int64",
        "signed_change_rate": "float64",
        "acc_trade_price_24h": "float64",
        "acc_trade_volume_24h": "float64",
    },
)
"""티커 스냅. 생산자 stream(Upbit ws)."""

FUNDING = EventSchema(
    columns=(
        "exchange",
        "symbol",
        "exchange_timestamp",
        "funding_rate",
    ),
    dtypes={"funding_rate": "float64"},
)
"""펀딩비. 생산자 collector(Binance fapi). Upbit 엔 선물 없어 Binance 기준."""

OPEN_INTEREST = EventSchema(
    columns=(
        "exchange",
        "symbol",
        "exchange_timestamp",
        "open_interest",
        "open_interest_value",
    ),
    dtypes={
        "open_interest": "float64",
        "open_interest_value": "float64",
    },
)
"""미결제약정. 생산자 collector(Binance fapi)."""

EVENT_SCHEMAS: dict[str, EventSchema] = {
    "trade": TRADE,
    "orderbook": ORDERBOOK,
    "ticker": TICKER,
    "funding": FUNDING,
    "open_interest": OPEN_INTEREST,
}
"""kind → :class:`EventSchema`. 키 집합은 :data:`EVENT_KINDS` 와 동일.

모든 kind 의 ``columns`` 는 :data:`EVENT_JOIN_KEY` 를 포함한다 (계약 불변식,
:func:`~tests` 에서 강제 검증).
"""
