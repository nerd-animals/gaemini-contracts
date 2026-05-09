"""KST 시간 표현 contract 가 모든 cross-repo 타입에서 동일한 약속을
가리키도록 고정한다 — strftime/strptime round-trip 으로 포맷이 살아있는지
까지 함께 검증한다.
"""
from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

from gaemini_contracts.schema import PARTITION_TIMEZONE
from gaemini_contracts.time import (
    KST_DATE_FORMAT,
    KST_MINUTE_FORMAT,
    KST_TIMESTAMP_FORMAT,
    KST_TIMEZONE,
)


def test_kst_timezone_label() -> None:
    assert KST_TIMEZONE == "Asia/Seoul"


def test_partition_timezone_aliases_kst() -> None:
    """OHLCV 전용 별칭은 단일 KST 약속을 가리켜야 한다."""
    assert PARTITION_TIMEZONE == KST_TIMEZONE


def test_zoneinfo_resolves() -> None:
    """라벨이 IANA tz 데이터베이스에 실제로 존재해야 한다."""
    ZoneInfo(KST_TIMEZONE)


def test_timestamp_format_round_trip() -> None:
    now_kst = datetime.now(ZoneInfo(KST_TIMEZONE)).replace(tzinfo=None)
    rendered = now_kst.strftime(KST_TIMESTAMP_FORMAT)
    parsed = datetime.strptime(rendered, KST_TIMESTAMP_FORMAT)
    assert parsed == now_kst


def test_timestamp_format_accepts_millisecond_padding() -> None:
    """과거 OrderBookSnapshot 포맷 (ms, 3 자리) 호환성 — strptime 은 ``%f``
    자리에서 1~6 자리를 모두 받아 부족한 자리를 0 으로 채운다."""
    parsed = datetime.strptime("2026-05-09 11:30:42.123", KST_TIMESTAMP_FORMAT)
    assert parsed.microsecond == 123_000


def test_date_format_round_trip() -> None:
    rendered = datetime(2026, 5, 3).strftime(KST_DATE_FORMAT)
    assert rendered == "2026-05-03"
    parsed = datetime.strptime(rendered, KST_DATE_FORMAT)
    assert (parsed.year, parsed.month, parsed.day) == (2026, 5, 3)


def test_minute_format_round_trip() -> None:
    rendered = datetime(2026, 5, 3, 9, 1).strftime(KST_MINUTE_FORMAT)
    assert rendered == "2026-05-03 09:01"
    parsed = datetime.strptime(rendered, KST_MINUTE_FORMAT)
    assert (parsed.year, parsed.month, parsed.day, parsed.hour, parsed.minute) == (
        2026,
        5,
        3,
        9,
        1,
    )
