"""애플리케이션 로그(JSONL) 파일의 경로 레이아웃.

생산자 (Producer)
    gaemini-core (StrategyLogger). 로그 한 건당 한 줄 append.

소비자 (Consumer)
    gaemini-view (로그 화면).

표준 레이아웃
    API 로그      ``{log_root}/_api/logs/{date}.jsonl``
    system 로그   ``{log_root}/{instance}/logs/{date}.jsonl``
    strategy 로그 ``{log_root}/{instance}/{strategy}/logs/{date}.jsonl``

예시
    >>> strategy_log_path(Path("/var/log/gaemini"), "paper-crypto", "momentum",
    ...          date(2026, 5, 3))
    PosixPath('/var/log/gaemini/paper-crypto/momentum/logs/2026-05-03.jsonl')

``instance`` 인자는 ``naming/instance.py``의 규칙으로 검증된다.
잘못된 이름이면 경로 생성 전에 ``InvalidInstanceName``이 발생한다.

용어
    instance : 실행 중인 gaemini-core 프로세스 한 벌의 이름. 예) "paper-crypto".
    strategy : 그 instance 안에 등록된 전략 이름.            예) "momentum".
"""
from __future__ import annotations

from datetime import date as Date
from pathlib import Path

from gaemini_contracts.naming.instance import validate_instance_name
from gaemini_contracts.naming.path_segment import validate_strategy_id


def api_log_path(log_root: Path, day: Date) -> Path:
    """Core API 프로세스의 일자별 JSONL 로그 파일 경로."""
    return log_root / "_api" / "logs" / f"{day.isoformat()}.jsonl"


def system_log_path(log_root: Path, instance: str, day: Date) -> Path:
    """한 instance 의 system 레벨 일자별 JSONL 로그 파일 경로."""
    validate_instance_name(instance)
    return log_root / instance / "logs" / f"{day.isoformat()}.jsonl"


def strategy_log_path(
    log_root: Path,
    instance: str,
    strategy: str,
    day: Date,
) -> Path:
    """한 strategy 의 일자별 JSONL 로그 파일 경로."""
    validate_instance_name(instance)
    validate_strategy_id(strategy)
    return log_root / instance / strategy / "logs" / f"{day.isoformat()}.jsonl"


def log_instance_dir(log_root: Path, instance: str) -> Path:
    """한 instance에 속한 모든 strategy 디렉토리의 부모."""
    validate_instance_name(instance)
    return log_root / instance


def log_strategy_dir(log_root: Path, instance: str, strategy: str) -> Path:
    """한 strategy 아래 ``logs/``, ``trades/`` 등이 모이는 부모 디렉토리."""
    validate_instance_name(instance)
    validate_strategy_id(strategy)
    return log_root / instance / strategy
