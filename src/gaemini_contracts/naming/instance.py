"""instance 이름 검증.

instance란
    실행 중인 gaemini-core 프로세스 한 벌의 이름.
    예) ``paper-crypto-momentum``, ``live-crypto``, ``paper-2``.

instance 이름은 다음 위치에 그대로 박힌다:
    - Redis 키 prefix       (``{instance}:strategy:{name}:...``)
    - 로그 디렉토리 경로     (``{log_root}/{instance}/...``)
    - 대시보드 URL

따라서 파일시스템에서도 URL에서도 안전해야 하고, Redis prefix
구분자인 콜론(":")과 충돌해서도 안 된다.

규칙
    ``^[a-z][a-z0-9-]{2,30}$``
        - 총 3 ~ 31자
        - 첫 글자는 영문 소문자
        - 영문 소문자 / 숫자 / 하이픈만 허용

운영 모드 prefix(``paper-`` / ``live-``)는 권장이지만 강제하지 않는다 —
가끔 짧은 이름의 일회성 실험을 돌려야 할 때가 있어서다.

예시
    유효:   "paper", "live", "paper-1", "paper-crypto-momentum"
    무효:   "Paper"     (대문자 불가)
            "1paper"    (숫자로 시작 불가)
            "paper_1"   (언더스코어 불가)
            "paper:1"   (콜론은 Redis prefix 파싱을 깨뜨림)
            "ab"        (3자 미만)
            "x" * 32    (31자 초과)
"""
from __future__ import annotations

import re

INSTANCE_NAME_PATTERN: re.Pattern[str] = re.compile(r"^[a-z][a-z0-9-]{2,30}$")


class InvalidInstanceName(ValueError):
    """instance 이름이 ``INSTANCE_NAME_PATTERN``을 만족하지 못할 때 발생."""


def validate_instance_name(name: str) -> None:
    """이름이 규칙을 어기면 ``InvalidInstanceName``을 던진다.

    instance를 인자로 받는 모든 경로/키 helper가 내부에서 이 함수를 호출하므로,
    잘못된 이름은 파일이나 Redis 키가 실제로 만들어지기 전 단계에서 실패한다.
    """
    if not isinstance(name, str):
        raise InvalidInstanceName(
            f"instance name must be str, got {type(name).__name__}"
        )
    if not INSTANCE_NAME_PATTERN.fullmatch(name):
        raise InvalidInstanceName(
            f"instance name {name!r} does not match {INSTANCE_NAME_PATTERN.pattern}"
        )
