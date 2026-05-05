"""거래 이력(JSONL) 파일의 경로 레이아웃.

한 줄 = 한 체결(또는 체결 시도) 이벤트 = 한 TradeRecord.

생산자 (Producer)
    gaemini-core. 체결/시도 이벤트가 있을 때마다 한 줄 append.

소비자 (Consumer)
    gaemini-view (거래 이력 화면).

표준 레이아웃
    ``{log_root}/{instance}/{strategy}/trades/{date}.jsonl``

거래 이력 파일은 일반 로그 디렉토리 안의 ``trades/`` 서브폴더에 자리한다.
즉 같은 (instance, strategy) 묶음 아래 일반 로그와 거래 로그가 함께 모이고,
둘 다 일자 기준으로 회전한다.

예시
    >>> trade_log_path(Path("/var/log/gaemini"), "paper-crypto", "momentum",
    ...                date(2026, 5, 3))
    PosixPath('/var/log/gaemini/paper-crypto/momentum/trades/2026-05-03.jsonl')

이 파일이 거래 이력의 정본이다 (과거 ``AccountState.orders_history`` 대체).

용어
    instance : 실행 중인 gaemini-core 프로세스 이름.
    strategy : 그 instance 안의 전략 이름.
    체결    : 주문이 거래소에서 실제로 매수/매도 성사된 것.
"""
from __future__ import annotations

from datetime import date as Date
from pathlib import Path

from gaemini_contracts.naming.instance import validate_instance_name


def trade_log_path(
    log_root: Path,
    instance: str,
    strategy: str,
    day: Date,
) -> Path:
    """(instance, strategy, day) 조합의 일자별 거래 이력 JSONL 경로."""
    validate_instance_name(instance)
    return log_root / instance / strategy / "trades" / f"{day.isoformat()}.jsonl"


def trades_dir(log_root: Path, instance: str, strategy: str) -> Path:
    """한 (instance, strategy)의 모든 일자별 거래 이력 파일이 모이는 디렉토리."""
    validate_instance_name(instance)
    return log_root / instance / strategy / "trades"
