"""OHLCV Parquet 컬럼 스키마와 파티션 정책.

생산자 (Producer)
    gaemini-data (시세 수집기). (시장, 종목, KST 날짜) 조합마다
    Parquet 파일 하나를 쓴다.

소비자 (Consumer)
    gaemini-core  — 전략의 데이터 로더.
    gaemini-view  — 차트 렌더링.

용어
    OHLCV    : 한 시간 구간의 시세 요약. Open / High / Low / Close / Volume
               (시가 / 고가 / 저가 / 종가 / 거래량).
    bar      : 한 시간 구간의 OHLCV 한 줄. "1분봉", "일봉" 등의 그 봉.
    Parquet  : 컬럼 기반 바이너리 파일 포맷. 시계열 분석에 흔히 쓴다.
    KST      : 한국 표준시 (UTC+9). KRX 거래일 기준의 시간대.
    KRX      : 한국거래소 (Korea Exchange).
    ticker   : 종목 식별자. 예) "KRW-BTC", "005930".
    market   : 시장 식별자. 예) "crypto", "krx".

파티션 키 계산은 writer/reader 모두 다음 순서로 통일한다.
    1) ``date`` 컬럼을 datetime으로 파싱.
    2) naive timestamp(시간대 정보 없는 값)는 UTC로 본다.
    3) Asia/Seoul로 변환.
    4) ``%Y-%m-%d`` 포맷으로 파일명을 만든다.

예시 파일 (경로 helper는 ``keys/parquet_path.py``)
    ``/cache/crypto/KRW-BTC/2026-05-03.parquet``       — 일봉
    ``/cache/crypto/KRW-BTC_1m/2026-05-03.parquet``    — 1분봉

샘플 row (아래 컬럼 순서)::

    date                  open       high       low        close      volume
    "2026-05-03"          50_000_000 51_200_000 49_800_000 50_900_000  123.4
    "2026-05-03 09:01"    50_010_000 50_050_000 49_990_000 50_030_000    1.2
"""
from __future__ import annotations

OHLCV_COLUMNS: tuple[str, ...] = (
    "date",     # str — 시각 (포맷은 아래 docstring 참조)
    "open",     # float — 구간 시가 (quote-asset 단위)
    "high",     # float — 구간 동안의 최고 거래가
    "low",      # float — 구간 동안의 최저 거래가
    "close",    # float — 구간 종가
    "volume",   # float — 구간 동안의 거래량 (base-asset 단위)
)
"""OHLCV Parquet 파티션의 표준 컬럼 순서.

``date`` 컬럼은 두 가지 포맷 중 하나의 문자열이다:
    ``YYYY-MM-DD``        — 일봉           예) "2026-05-03"
    ``YYYY-MM-DD HH:MM``  — 분봉(분 단위)  예) "2026-05-03 09:01"

pandas Timestamp가 아니라 문자열로 두는 이유:
    - Parquet/Arrow의 string 컬럼은 언어 런타임을 가리지 않고 portable하다.
    - 스키마 버전이 바뀌어도 영향이 적다.
"""

PARTITION_TIMEZONE = "Asia/Seoul"
"""KST (UTC+9). 파일 경계는 KST 자정 기준이지 UTC 자정이 아니다.

이유: KRX와 한국 사용자의 거래일은 Asia/Seoul 기준이다.
파일 ``2026-05-03.parquet``에는 UTC 날짜와 무관하게
"KST 달력으로 2026-05-03인 모든 bar"가 들어간다.
"""

PARTITION_GRANULARITY = "day"
"""(시장, 종목, KST 날짜) 조합마다 Parquet 파일 하나."""

MINUTE_SYMBOL_SUFFIX = "_1m"
"""1분봉 종목명에 붙이는 접미사.

    KRW-BTC 일봉   →  ``crypto/KRW-BTC/...``
    KRW-BTC 1분봉 →  ``crypto/KRW-BTC_1m/...``

"한 종목 = 한 디렉토리" 규칙을 유지하면서 같은 종목의 여러 시간 단위를
별도 디렉토리로 분리하기 위함이다.
"""
