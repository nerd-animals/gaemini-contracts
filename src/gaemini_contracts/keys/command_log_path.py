"""명령 audit(JSONL) 파일의 경로 레이아웃."""
from __future__ import annotations

from datetime import date as Date
from pathlib import Path

from gaemini_contracts.naming.instance import validate_instance_name


def command_log_path(log_root: Path, instance: str, day: Date) -> Path:
    """한 instance 의 일자별 command audit JSONL 경로."""
    validate_instance_name(instance)
    return log_root / instance / "commands" / f"{day.isoformat()}.jsonl"


def command_logs_dir(log_root: Path, instance: str) -> Path:
    """한 instance 의 command audit 파일이 모이는 디렉토리."""
    validate_instance_name(instance)
    return log_root / instance / "commands"
