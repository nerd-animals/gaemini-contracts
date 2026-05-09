"""Cross-repo 시간 표현 계약.

이 패키지의 모든 시간 필드는 **KST (Asia/Seoul) naive 문자열**이다.
UTC↔KST 변환은 producer 진입 시점에 한 번만 수행하고, 그 뒤로는 어떤
경계(JSONL 파일, Redis msgpack, Parquet 컬럼)에서도 다시 변환하지 않는다.

이유
    1차 시장이 KRX 와 한국 거래쌍 (예: ``KRW-BTC``) 이라 UTC 경유 단계는
    잉여이다. KST 단일 timezone 가정을 contract 전반에 박아두어 producer/
    consumer 가 매번 "이 필드 timezone 이 뭐였지?" 를 확인하지 않게 한다.

    naive 문자열을 쓰는 이유는
        (1) JSON / Parquet / msgpack 모두 portable 하고,
        (2) timezone 정보가 빠져 있어도 KST 라는 고정 약속이 있어서 모호함이
            없으며,
        (3) 거래소 응답 raw 가 KST 가 아닐 때 변환 책임을 producer 진입점에
            1회로 모을 수 있기 때문이다.

해외 거래소를 추가할 때
    이 가정을 유지한다 — producer 가 자기 진입 시점에 KST 로 변환해서
    contract 안에 들여보낸다. 변환 책임은 contract 바깥에 둔다.

용어
    KST       : 한국 표준시 (UTC+9). DST 없음.
    naive     : timezone 정보가 붙어 있지 않은 시간값.
    Asia/Seoul: IANA timezone 데이터베이스 식별자.
"""
from __future__ import annotations

KST_TIMEZONE = "Asia/Seoul"
"""KST naive 시간 필드가 해석되는 시간대.

이 상수는 *변환 입력* 이 아니라 *해석 라벨* 이다. contracts 안의 어떤
helper 도 timezone 변환을 수행하지 않는다 — 이미 KST 로 기록된 문자열을
그대로 KST 로 해석한다는 약속을 명시할 뿐이다.
"""

KST_TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S.%f"
"""ms 이상 정밀도가 필요한 시각 필드의 포맷.

쓰임:
    ``LogRecord.ts``
    ``TradeRecord.ts``
    ``OrderBookSnapshot.exchange_timestamp`` / ``received_at`` /
    ``previous_received_at``

Python ``datetime.strftime`` 표현. ``%f`` 는 6 자리 microsecond 로 zero-padded.
예) ``"2026-05-09 11:30:42.123456"``.

``strptime`` 은 ``%f`` 자리에서 1~6 자리 모두 받아주므로 (부족한 자리는
0 으로 padded), 과거에 ms (3 자리) 로 기록된 데이터도 reader 호환된다.
다만 새 producer 는 ``strftime`` 의 기본값인 microsecond 6 자리를 그대로
쓰는 것을 권장한다.

producer 코드 예::

    from datetime import datetime
    from zoneinfo import ZoneInfo
    from gaemini_contracts.time import KST_TIMESTAMP_FORMAT, KST_TIMEZONE

    now_kst = datetime.now(ZoneInfo(KST_TIMEZONE)).replace(tzinfo=None)
    ts = now_kst.strftime(KST_TIMESTAMP_FORMAT)
"""

KST_DATE_FORMAT = "%Y-%m-%d"
"""일 단위 시각 필드의 포맷.

쓰임:
    ``OHLCV.date`` 컬럼의 일봉 표현. 예) ``"2026-05-03"``.
"""

KST_MINUTE_FORMAT = "%Y-%m-%d %H:%M"
"""분 단위 시각 필드의 포맷.

쓰임:
    ``OHLCV.date`` 컬럼의 분봉 표현. 예) ``"2026-05-03 09:01"``.
"""
