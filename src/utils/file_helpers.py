# -*- coding: utf-8 -*-
"""
파일 백업/복원 헬퍼 함수
"""

import shutil
from pathlib import Path
from datetime import datetime
from typing import Tuple, Optional


def backup_database(db_path: Path, backup_dir: Path) -> Tuple[bool, Optional[str], Optional[str]]:
    """데이터베이스 파일 백업

    Args:
        db_path: 백업할 데이터베이스 파일 경로
        backup_dir: 백업 파일을 저장할 디렉토리

    Returns:
        (성공 여부, 백업 파일 경로, 에러 메시지)
        성공 시: (True, "백업 파일 경로", None)
        실패 시: (False, None, "에러 메시지")
    """
    try:
        # 원본 파일 존재 확인
        if not db_path.exists():
            return (False, None, "데이터베이스 파일을 찾을 수 없습니다.")

        # 백업 디렉토리 생성
        backup_dir.mkdir(parents=True, exist_ok=True)

        # 백업 파일명 생성 (crm_backup_YYYYMMDD_HHMMSS.db)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"crm_backup_{timestamp}.db"
        backup_path = backup_dir / backup_filename

        # 파일 복사
        shutil.copy2(db_path, backup_path)

        return (True, str(backup_path), None)

    except PermissionError:
        return (False, None, "파일 접근 권한이 없습니다.")
    except Exception as e:
        return (False, None, f"백업 실패: {str(e)}")


def restore_database(backup_path: Path, db_path: Path) -> Tuple[bool, Optional[str]]:
    """백업 파일로부터 데이터베이스 복원

    Args:
        backup_path: 백업 파일 경로
        db_path: 복원할 데이터베이스 파일 경로

    Returns:
        (성공 여부, 에러 메시지)
        성공 시: (True, None)
        실패 시: (False, "에러 메시지")
    """
    try:
        # 백업 파일 존재 확인
        if not backup_path.exists():
            return (False, "백업 파일을 찾을 수 없습니다.")

        # 기존 DB 파일 백업 (복원 전 안전 조치)
        temp_backup = None
        if db_path.exists():
            temp_backup = db_path.parent / f"{db_path.name}.before_restore"
            shutil.copy2(db_path, temp_backup)

        # 백업 파일로 덮어쓰기
        shutil.copy2(backup_path, db_path)

        # 임시 백업 파일 삭제
        if temp_backup and temp_backup.exists():
            temp_backup.unlink()

        return (True, None)

    except PermissionError:
        return (False, "파일 접근 권한이 없습니다.")
    except Exception as e:
        return (False, f"복원 실패: {str(e)}")


def get_backup_info(backup_path: Path) -> dict:
    """백업 파일 정보 조회

    Args:
        backup_path: 백업 파일 경로

    Returns:
        백업 파일 정보 딕셔너리
    """
    if not backup_path.exists():
        return {}

    stat = backup_path.stat()
    return {
        'filename': backup_path.name,
        'size': stat.st_size,
        'created': datetime.fromtimestamp(stat.st_ctime).strftime("%Y-%m-%d %H:%M:%S"),
        'modified': datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
    }
