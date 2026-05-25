"""파일 경로 segment 검증.

contracts 의 path helper 는 외부 repo 가 넘긴 식별자를 그대로 디렉토리 이름에
쓴다. 따라서 traversal 이나 빈 segment 는 helper 경계에서 거부한다.
"""
from __future__ import annotations

import re

STRATEGY_ID_PATTERN: re.Pattern[str] = re.compile(r"^[a-z][a-z0-9-]*$")


class InvalidPathSegment(ValueError):
    """경로 segment 로 쓰기에 안전하지 않은 값일 때 발생."""


class InvalidStrategyId(InvalidPathSegment):
    """strategy id 가 contracts 의 경로 규칙을 만족하지 못할 때 발생."""


def validate_path_segment(value: str, field_name: str) -> None:
    """``value`` 가 단일 경로 segment 로 안전한지 확인한다.

    exchange/symbol/market/ticker 처럼 도메인마다 문자 규칙이 다른 값은 좁은
    regex 대신 traversal 방어만 공통 적용한다.
    """
    if not isinstance(value, str):
        raise InvalidPathSegment(
            f"{field_name} must be str, got {type(value).__name__}"
        )
    if value in {"", ".", ".."}:
        raise InvalidPathSegment(f"{field_name} must be a non-empty path segment")
    if "/" in value or "\\" in value or "\0" in value:
        raise InvalidPathSegment(f"{field_name} contains an unsafe path separator")


def validate_strategy_id(strategy_id: str) -> None:
    """strategy id 는 instance name 과 같은 소문자/숫자/하이픈 계열을 쓴다."""
    try:
        validate_path_segment(strategy_id, "strategy_id")
    except InvalidPathSegment as exc:
        raise InvalidStrategyId(str(exc)) from exc
    if not STRATEGY_ID_PATTERN.fullmatch(strategy_id):
        raise InvalidStrategyId(
            f"strategy_id {strategy_id!r} does not match {STRATEGY_ID_PATTERN.pattern}"
        )
