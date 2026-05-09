"""OrderBookSnapshot — 거래소 호가창 한 시점의 정규화된 스냅샷.

생산자 (Producer)
    gaemini-data (stream gateway). 거래소 WebSocket orderbook 채널에서
    받은 raw payload 를 정규화해 Redis 에 SET 한다.

소비자 (Consumer)
    gaemini-core, gaemini-view. Redis client 로 GET 해서 사용.

저장 위치
    Redis key ``orderbook:{exchange}:{market}`` (예: ``orderbook:upbit:KRW-BTC``).
    값은 msgpack 직렬화. TTL 5초 (생산자가 5초 안에 갱신 못 하면 키가 사라져
    소비자가 stale state 로 의사결정하는 것을 방지).

LogRecord/TradeRecord 와의 차이
    저 둘은 JSONL append-only 디스크 파일이고 이 타입은 in-memory state cache.
    그러나 schema_version 은 동일하게 들고 다닌다 — 형태가 바뀌면 producer 와
    consumer 가 동시 배포되어야 하므로 fail-fast 로 막는다.

시간 기준
    두 시각을 모두 들고 다닌다. *어느 쪽으로 의사결정할지는 consumer 가
    선택*하지만, paper-live 일치성을 위해 ``received_at`` 기준 권장.
        exchange_timestamp — 거래소가 publish 한 시각 (시장 분석 용도)
        received_at        — gaemini-data 가 ws 로 받은 시각 (의사결정 용도)
    둘 다 KST naive ``"YYYY-MM-DD HH:MM:SS.fff"`` 문자열.

gap 처리
    ``has_gap=True`` 는 직전 connection 이 끊긴 뒤 처음 받은 snapshot 을 의미.
    이 사이 기간 동안 시장이 어떻게 움직였는지 알 수 없으므로 consumer 는
    이 flag 가 true 인 snapshot 을 보면 strategy state 를 reset 하거나 의사결정을
    skip 해야 한다. 직전 정상 snapshot 의 ``received_at`` 은
    ``previous_received_at`` 으로 노출되어 gap 길이를 계산할 수 있다.

용어
    bid       : 매수 호가. 가격 내림차순으로 정렬 (가장 높은 매수가가 [0]).
    ask       : 매도 호가. 가격 오름차순으로 정렬 (가장 낮은 매도가가 [0]).
    depth     : bids/asks 각 리스트 길이. Upbit ws orderbook 은 보통 15.
    snapshot  : "이 시점에 본 호가의 전체 모습". L2 delta 와 달리 매번 전체.

예시 (msgpack 디시리얼라이즈 후)::

    {
        "schema_version": 1,
        "exchange": "upbit",
        "market": "KRW-BTC",
        "exchange_timestamp": "2026-05-09 11:30:42.123",
        "received_at": "2026-05-09 11:30:42.198",
        "depth": 15,
        "bids": [{"price": 50_000_000.0, "size": 0.123}, ...],
        "asks": [{"price": 50_010_000.0, "size": 0.456}, ...],
        "has_gap": False,
        "previous_received_at": None,
    }
"""
from __future__ import annotations

from typing import TypedDict

# OrderBookSnapshot 의 형태가 깨지는 변경(필드 이름 변경/제거, 타입 좁힘)이
# 있을 때마다 1씩 올린다. producer 와 consumer 의 contracts 버전이 다르면
# 즉시 SchemaIncompatible 로 거부 — Redis 에 잘못된 형태로 SET 되는 것을 막는다.
ORDER_BOOK_SNAPSHOT_VERSION = 1


class OrderBookLevel(TypedDict):
    """호가 한 단계. 가격과 그 가격에 누적된 수량."""

    # 가격. quote-asset 단위 (KRW-BTC 면 KRW).
    price: float

    # 그 가격에 쌓인 base-asset 수량 (KRW-BTC 면 BTC).
    size: float


class OrderBookSnapshot(TypedDict):
    schema_version: int

    # 거래소 식별자. 소문자. 예) "upbit".
    exchange: str

    # 종목 식별자. 거래소가 쓰는 형식 그대로. 예) "KRW-BTC".
    market: str

    # 거래소가 publish 한 시각. KST naive "YYYY-MM-DD HH:MM:SS.fff".
    # 거래소가 ms 미만 정밀도를 안 주면 ".000" 으로 채운다.
    exchange_timestamp: str

    # gaemini-data 가 ws 로 받은 시각. KST naive "YYYY-MM-DD HH:MM:SS.fff".
    # 의사결정 시각으로 권장 — paper-live 의 latency 모델이 일치하기 때문.
    received_at: str

    # bids 와 asks 의 길이. 둘이 다를 수 있으나 Upbit 는 보통 15 로 동일.
    depth: int

    # 매수 호가. 가격 *내림차순* — bids[0] 이 가장 높은 매수가.
    bids: list[OrderBookLevel]

    # 매도 호가. 가격 *오름차순* — asks[0] 이 가장 낮은 매도가.
    asks: list[OrderBookLevel]

    # 직전 ws disconnect 이후 첫 snapshot 이면 True. 자세한 의미는 module
    # docstring 의 "gap 처리" 섹션 참조.
    has_gap: bool

    # has_gap=True 일 때, 직전 정상 snapshot 의 received_at.
    # gap 길이 계산 또는 로깅 용도. has_gap=False 면 None.
    previous_received_at: str | None
