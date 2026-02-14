# -*- coding: utf-8 -*-
"""
입력 검증 함수
"""

import re
from datetime import datetime
from typing import Tuple, Optional


def validate_phone(phone: str) -> Tuple[bool, Optional[str]]:
    """전화번호 형식 검증

    Args:
        phone: 검증할 전화번호

    Returns:
        (검증 성공 여부, 에러 메시지)
        성공 시: (True, None)
        실패 시: (False, "에러 메시지")

    Example:
        >>> validate_phone("010-1234-5678")
        (True, None)
        >>> validate_phone("invalid")
        (False, "유효하지 않은 전화번호 형식입니다")
    """
    if not phone or not phone.strip():
        return (False, "전화번호는 필수 항목입니다")

    # 하이픈 포함/미포함 모두 허용
    # 형식: 010-1234-5678, 01012345678, 02-1234-5678 등
    pattern = r'^\d{2,3}-?\d{3,4}-?\d{4}$'

    if not re.match(pattern, phone):
        return (False, "유효하지 않은 전화번호 형식입니다 (예: 010-1234-5678)")

    return (True, None)


def validate_email(email: str) -> Tuple[bool, Optional[str]]:
    """이메일 형식 검증

    Args:
        email: 검증할 이메일

    Returns:
        (검증 성공 여부, 에러 메시지)

    Example:
        >>> validate_email("test@example.com")
        (True, None)
        >>> validate_email("invalid")
        (False, "유효하지 않은 이메일 형식입니다")
    """
    # 빈 값은 선택 필드이므로 허용
    if not email or not email.strip():
        return (True, None)

    # 기본 이메일 정규식
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

    if not re.match(pattern, email):
        return (False, "유효하지 않은 이메일 형식입니다 (예: example@email.com)")

    return (True, None)


def validate_birth_date(date_str: str) -> Tuple[bool, Optional[str]]:
    """생년월일 형식 검증

    Args:
        date_str: 검증할 생년월일 (YYYY-MM-DD 형식)

    Returns:
        (검증 성공 여부, 에러 메시지)

    Example:
        >>> validate_birth_date("1990-01-15")
        (True, None)
        >>> validate_birth_date("2023-13-01")
        (False, "유효하지 않은 날짜입니다")
    """
    # 빈 값은 선택 필드이므로 허용
    if not date_str or not date_str.strip():
        return (True, None)

    # YYYY-MM-DD 형식 확인
    pattern = r'^\d{4}-\d{2}-\d{2}$'

    if not re.match(pattern, date_str):
        return (False, "날짜 형식이 올바르지 않습니다 (예: 1990-01-15)")

    # 실제 날짜 유효성 확인
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        return (False, "유효하지 않은 날짜입니다")

    return (True, None)


def validate_name(name: str) -> Tuple[bool, Optional[str]]:
    """이름 검증

    Args:
        name: 검증할 이름

    Returns:
        (검증 성공 여부, 에러 메시지)
    """
    if not name or not name.strip():
        return (False, "이름은 필수 항목입니다")

    if len(name.strip()) < 1:
        return (False, "이름을 입력해주세요")

    return (True, None)


def validate_resident_id(resident_id: str) -> Tuple[bool, Optional[str]]:
    """주민등록번호 형식 검증

    Args:
        resident_id: 검증할 주민등록번호 (NNNNNN-NNNNNNN 형식)

    Returns:
        (검증 성공 여부, 에러 메시지)
        성공 시: (True, None)
        실패 시: (False, "에러 메시지")

    Example:
        >>> validate_resident_id("900115-1234567")
        (True, None)
        >>> validate_resident_id("900115")
        (False, "유효하지 않은 주민등록번호 형식입니다")
    """
    if not resident_id or not resident_id.strip():
        return (False, "주민등록번호는 필수 항목입니다")

    # 하이픈 포함 NNNNNN-NNNNNNN 형식 (총 13자리 숫자 + 하이픈 1개)
    pattern = r'^\d{6}-\d{7}$'

    if not re.match(pattern, resident_id):
        return (False, "유효하지 않은 주민등록번호 형식입니다 (예: 900115-1234567)")

    # 하이픈 제거 후 13자리 확인
    digits_only = resident_id.replace("-", "")
    if len(digits_only) != 13:
        return (False, "주민등록번호는 13자리여야 합니다")

    return (True, None)
