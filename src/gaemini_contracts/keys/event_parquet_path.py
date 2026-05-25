"""이벤트 Parquet 파일의 경로 레이아웃.

OHLCV 경로(:mod:`gaemini_contracts.keys.parquet_path`)와 별개인, 고빈도
이벤트 데이터(체결·호가·티커·펀딩·OI·거시 관측)의 경로 단일 진실 공급원.
컬럼/dtype 스키마는 :mod:`gaemini_contracts.schema.event` 참조.

생산자 (Producer)
    gaemini-data. :class:`EventParquetWriter` 가 라이브 조각으로 append,
    별도 컴팩션 잡이 일 1 파일로 병합.

소비자 (Consumer)
    gaemini-core, gaemini-view.

생애주기 2 단계 레이아웃
    라이브 조각 ::

        {base}/{kind}/{exchange}/{symbol}/{YYYY-MM-DD}/part-*.parquet

    컴팩션 후 (그 날의 권위 있는 완본) ::

        {base}/{kind}/{exchange}/{symbol}/{YYYY-MM-DD}.parquet

    한 날짜에 컴팩션 완본이 있으면 그것이 정본이고 조각 디렉터리는 무시
    (크래시로 완본 생성 후 조각 미삭제 시 중복 방지).

자리마다 내용물 그대로
    ``{exchange}``/``{symbol}`` 자리 값은 각 row 의 ``exchange``/``symbol``
    컬럼 값과 글자까지 동일하다 — 소비자는 경로만 보고 조인 키를 안다.
    (OHLCV 의 ``market``="crypto"(자산군)와 달리, 여기 두 번째 자리는
    거래소이므로 이름이 ``exchange``.)

``base``\\는 호출자가 (보통 환경변수에서) 넘긴다. 이 모듈은
``{kind}/{exchange}/{symbol}/...`` 부분만 책임진다.

용어
    kind     : 이벤트 종류 (단수). :data:`EVENT_KINDS` 중 하나.
    exchange : 거래소 식별자. 소문자. 예) "upbit", "binance". 거래소가 아닌
               데이터 소스(거시 제공처)는 소스 id — 예) "fred", "bok".
    symbol   : 거래소 원형 심볼. 예) "KRW-BTC", "BTCUSDT". 거시는 소스
               시리즈 ID — 예) "DGS10".

예시
    >>> event_day_file(Path("/data"), "trade", "upbit", "KRW-BTC",
    ...                 date(2026, 5, 17))
    PosixPath('/data/trade/upbit/KRW-BTC/2026-05-17.parquet')
"""
from __future__ import annotations

from datetime import date as Date
from datetime import timedelta
from pathlib import Path

from gaemini_contracts.naming.path_segment import validate_path_segment
from gaemini_contracts.schema.event import EVENT_KINDS

EVENT_FRAGMENT_GLOB = "part-*.parquet"
"""한 날짜 조각 디렉터리 안의 라이브 조각 glob.

조각 파일명(``part-{seq}-{ms}.parquet``)의 seq/ms 는 producer 사적 detail.
소비자는 이 glob 으로만 조각을 모은다 (파일명 규칙을 하드코딩하지 않는다).
"""


class InvalidEventKind(ValueError):
    """``kind`` 가 :data:`EVENT_KINDS` 에 없을 때."""


def validate_event_kind(kind: str) -> None:
    """contracts 가 소유한 kind 네임스페이스 밖이면 거부.

    경로가 잘못된 kind 로 갈라지면 소비자가 데이터를 영영 못 찾으므로
    경로 생성 시점에 fail-fast.
    """
    if kind not in EVENT_KINDS:
        raise InvalidEventKind(
            f"unknown event kind {kind!r}; allowed: {', '.join(EVENT_KINDS)}"
        )


def event_symbol_dir(
    base: Path,
    kind: str,
    exchange: str,
    symbol: str,
) -> Path:
    """한 (kind, exchange, symbol) 의 모든 일자 데이터가 모이는 디렉토리.

    예) ``/data/trade/upbit/KRW-BTC``.
    """
    validate_event_kind(kind)
    validate_path_segment(exchange, "exchange")
    validate_path_segment(symbol, "symbol")
    return base / kind / exchange / symbol


def event_day_file(
    base: Path,
    kind: str,
    exchange: str,
    symbol: str,
    day: Date,
) -> Path:
    """컴팩션 후 그 날의 권위 있는 완본 Parquet 경로.

    예) ``/data/trade/upbit/KRW-BTC/2026-05-17.parquet``.
    """
    return event_symbol_dir(base, kind, exchange, symbol) / f"{day.isoformat()}.parquet"


def event_fragment_dir(
    base: Path,
    kind: str,
    exchange: str,
    symbol: str,
    day: Date,
) -> Path:
    """라이브 조각이 쌓이는 그 날의 디렉토리 (컴팩션 전).

    안의 조각은 :data:`EVENT_FRAGMENT_GLOB` 로 모은다.
    예) ``/data/trade/upbit/KRW-BTC/2026-05-17/``.
    """
    return event_symbol_dir(base, kind, exchange, symbol) / day.isoformat()


def event_partition_paths(
    base: Path,
    kind: str,
    exchange: str,
    symbol: str,
    start: Date | None = None,
    end: Date | None = None,
) -> list[Path]:
    """읽어야 할 event Parquet path 를 날짜순으로 반환한다.

    한 날짜에 ``YYYY-MM-DD.parquet`` 완본이 있으면 그 파일만 반환하고,
    같은 날짜의 fragment directory 는 무시한다. 완본이 없으면
    ``YYYY-MM-DD/part-*.parquet`` 조각을 파일명순으로 반환한다.

    ``start``/``end`` 는 inclusive 이다. 둘 다 없으면 symbol directory 에서
    발견되는 날짜를 스캔한다.
    """
    if start is not None and end is not None and start > end:
        raise ValueError(
            f"start must be <= end, got {start.isoformat()} > {end.isoformat()}"
        )

    days = _event_partition_days(base, kind, exchange, symbol, start, end)
    paths: list[Path] = []
    for day in days:
        day_file = event_day_file(base, kind, exchange, symbol, day)
        if day_file.is_file():
            paths.append(day_file)
            continue

        fragment_dir = event_fragment_dir(base, kind, exchange, symbol, day)
        if fragment_dir.is_dir():
            paths.extend(
                sorted(p for p in fragment_dir.glob(EVENT_FRAGMENT_GLOB) if p.is_file())
            )
    return paths


def _event_partition_days(
    base: Path,
    kind: str,
    exchange: str,
    symbol: str,
    start: Date | None,
    end: Date | None,
) -> list[Date]:
    if start is not None and end is not None:
        return [start + timedelta(days=i) for i in range((end - start).days + 1)]

    symbol_dir = event_symbol_dir(base, kind, exchange, symbol)
    discovered: set[Date] = set()
    if symbol_dir.is_dir():
        for child in symbol_dir.iterdir():
            day = _date_from_partition_name(child)
            if day is None:
                continue
            if start is not None and day < start:
                continue
            if end is not None and day > end:
                continue
            discovered.add(day)
    return sorted(discovered)


def _date_from_partition_name(path: Path) -> Date | None:
    if path.is_file() and path.suffix == ".parquet":
        name = path.stem
    elif path.is_dir():
        name = path.name
    else:
        return None

    try:
        return Date.fromisoformat(name)
    except ValueError:
        return None
