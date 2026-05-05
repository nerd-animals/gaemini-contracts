"""TradeRecord — 체결(또는 체결 시도) 이벤트 한 건. JSONL append-only.

생산자 (Producer)
    gaemini-core. 거래소가 응답을 줄 때마다 한 줄을 append한다.
    체결이 성공한 경우뿐 아니라 "실패", "취소"도 한 줄로 남는다.

소비자 (Consumer)
    gaemini-view (거래 이력 화면). 한 줄씩 다음 함수로 파싱한다::

        parse_versioned_json(line, TRADE_RECORD_VERSION, "TradeRecord")

파일 경로 (``keys/trade_log_path.py`` 참조)
    ``{log_root}/{instance}/{strategy}/trades/{date}.jsonl``
    경로에 (instance, strategy)가 이미 박혀 있으므로 레코드 안에는
    중복으로 넣지 않는다.

진실 공급원 (source of truth)
    이 파일이 거래 이력의 정본이다. 과거에 ``AccountState.orders_history``
    리스트로 들고 있던 정보를 이 파일이 대체한다.

쓰기 순서 (권장)
    1) 이 JSONL 파일에 한 줄 append.
    2) Redis ``AccountState`` 갱신 (현금/포지션 반영).
    파일 → Redis 순서이므로, Redis 갱신이 실패해도 파일에서 복구 가능하다.

용어
    체결 (fill)        : 주문이 거래소에서 실제로 매수/매도 성사된 것.
    부분 체결 (partial) : 주문 수량 중 일부만 체결되고 나머지는 대기/취소된 상태.
    base-asset         : 거래쌍에서 사고팔리는 자산. KRW-BTC면 BTC가 base.
    quote-asset        : 그 자산을 가격 매기는 통화. KRW-BTC면 KRW가 quote.
    수수료 (fee)        : 거래소에 지불하는 비용. quote-asset 단위.
    티커 (ticker)       : 종목 식별 문자열. 시장마다 형식이 다르다.
                         예) crypto: "KRW-BTC", "USDT-ETH" / KRX: "005930"

예시 줄::

    {"schema_version": 1, "ts": "2026-05-03T08:01:31+00:00",
     "order_id": "o-42", "ticker": "KRW-BTC", "side": "buy",
     "filled_amount": 0.01, "filled_price": 50000000.0,
     "fee": 25.0, "status": "filled"}
"""
from __future__ import annotations

from typing import Literal, TypedDict

# TradeRecord 형태가 깨지는 변경이 있을 때마다 1씩 올린다.
# 읽는 쪽은 schema_version이 이 값과 다르면 줄을 거부한다.
TRADE_RECORD_VERSION = 1


class TradeRecord(TypedDict):
    schema_version: int

    # 거래소 응답 시각. UTC ISO 8601.
    # 예) "2026-05-03T08:01:31+00:00"
    ts: str

    # 거래소가 발급한 주문 ID. 거래소 안에서만 unique. 의미는 들여다보지 않는다.
    order_id: str

    # 종목 식별자. 시장 형식에 따른다 (위 "용어" 참조).
    ticker: str

    # 매수/매도 방향. ("hold"는 전략 단계 개념이고 거래 기록에는 등장하지 않는다.)
    side: Literal["buy", "sell"]

    # 이 이벤트로 체결된 수량. base-asset 단위(현금이 아님).
    # 항상 0 이상. 부분 체결인 경우 이번에 체결된 분량만 들어가고,
    # 나머지는 추가 TradeRecord(또는 "cancelled" 레코드)로 따라온다.
    filled_amount: float

    # 이 이벤트의 체결 평균 단가. base-asset 한 단위당 quote-asset 가격.
    # status가 "failed" 또는 "cancelled"라 체결이 없었다면 0.0.
    filled_price: float

    # 이번 체결 이벤트에 대해 거래소에 낸 수수료. quote-asset 단위.
    fee: float

    # 이 이벤트의 결과. "주문 한 건의 전체 라이프사이클"이 아니라
    # "이번 한 이벤트"의 결과만 담는다.
    # 따라서 부분 체결 후 잔량 취소된 주문은 두 줄로 기록된다
    # ("partial" 한 줄 + "cancelled" 한 줄).
    #   "filled"    — 이번 이벤트로 전량 체결.
    #   "partial"   — 부분 체결. 이후 추가 이벤트가 더 있을 수 있음.
    #   "failed"    — 거래소 거절 (잔고 부족, 잘못된 주문 등).
    #   "cancelled" — 추가 체결 없이 취소됨.
    status: Literal["filled", "partial", "failed", "cancelled"]
