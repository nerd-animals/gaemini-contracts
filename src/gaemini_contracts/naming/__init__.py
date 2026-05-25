"""instance 이름 검증.

instance란 실행 중인 gaemini-core 프로세스 한 벌의 이름이다
(예: ``paper-crypto``, ``live-crypto``). 이 이름이 Redis prefix, 로그 경로,
대시보드 URL에 그대로 박히므로 파일시스템에서도 URL에서도 안전해야 한다.

규칙과 예시는 :mod:`gaemini_contracts.naming.instance` 참조.
"""
from gaemini_contracts.naming.instance import (
    INSTANCE_NAME_PATTERN,
    InvalidInstanceName,
    validate_instance_name,
)
from gaemini_contracts.naming.path_segment import (
    STRATEGY_ID_PATTERN,
    InvalidPathSegment,
    InvalidStrategyId,
    validate_path_segment,
    validate_strategy_id,
)

__all__ = [
    "INSTANCE_NAME_PATTERN",
    "STRATEGY_ID_PATTERN",
    "InvalidInstanceName",
    "InvalidPathSegment",
    "InvalidStrategyId",
    "validate_instance_name",
    "validate_path_segment",
    "validate_strategy_id",
]
