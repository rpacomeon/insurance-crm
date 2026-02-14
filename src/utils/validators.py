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


def validate_premium(premium_str: str) -> Tuple[bool, Optional[str]]:
    """보험료 검증

    Args:
        premium_str: 검증할 보험료 (문자열)

    Returns:
        (검증 성공 여부, 에러 메시지)
        성공 시: (True, None)
        실패 시: (False, "에러 메시지")

    Example:
        >>> validate_premium("50000")
        (True, None)
        >>> validate_premium("abc")
        (False, "보험료는 숫자여야 합니다")
    """
    if not premium_str or not premium_str.strip():
        return (False, "보험료는 필수 항목입니다")

    # 쉼표 제거 (예: "50,000" -> "50000")
    premium_str = premium_str.replace(",", "").strip()

    # 숫자 검증
    try:
        premium = int(premium_str)
    except ValueError:
        return (False, "보험료는 숫자여야 합니다")

    # 범위 검증 (0 < premium <= 100,000,000)
    if premium <= 0:
        return (False, "보험료는 0보다 커야 합니다")

    if premium > 100_000_000:
        return (False, "보험료는 1억원 이하여야 합니다")

    return (True, None)


def validate_billing_day(day_str: str) -> Tuple[bool, Optional[str]]:
    """납부일 검증

    Args:
        day_str: 검증할 납부일 (문자열)

    Returns:
        (검증 성공 여부, 에러 메시지)
        성공 시: (True, None)
        실패 시: (False, "에러 메시지")

    Example:
        >>> validate_billing_day("25")
        (True, None)
        >>> validate_billing_day("32")
        (False, "납부일은 1~31 사이여야 합니다")
    """
    if not day_str or not day_str.strip():
        return (False, "납부일은 필수 항목입니다")

    # 숫자 검증
    try:
        day = int(day_str)
    except ValueError:
        return (False, "납부일은 숫자여야 합니다")

    # 범위 검증 (1~31)
    if day < 1 or day > 31:
        return (False, "납부일은 1~31 사이여야 합니다")

    return (True, None)


def validate_contract_dates(start_date: str, end_date: Optional[str]) -> Tuple[bool, Optional[str]]:
    """계약 시작일/종료일 검증

    Args:
        start_date: 계약 시작일 (YYYY-MM-DD 형식, 필수)
        end_date: 계약 종료일 (YYYY-MM-DD 형식, 선택)

    Returns:
        (검증 성공 여부, 에러 메시지)
        성공 시: (True, None)
        실패 시: (False, "에러 메시지")

    Example:
        >>> validate_contract_dates("2026-01-01", "2027-01-01")
        (True, None)
        >>> validate_contract_dates("2026-01-01", "2025-01-01")
        (False, "종료일은 시작일보다 이후여야 합니다")
    """
    # 시작일 필수 검증
    if not start_date or not start_date.strip():
        return (False, "계약 시작일은 필수 항목입니다")

    # 시작일 형식 검증
    is_valid, error_msg = validate_birth_date(start_date)
    if not is_valid:
        return (False, f"시작일: {error_msg}")

    # 종료일 선택 필드 (빈 값 허용)
    if not end_date or not end_date.strip():
        return (True, None)

    # 종료일 형식 검증
    is_valid, error_msg = validate_birth_date(end_date)
    if not is_valid:
        return (False, f"종료일: {error_msg}")

    # 시작일 <= 종료일 검증
    try:
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")

        if end_dt < start_dt:
            return (False, "종료일은 시작일보다 이후여야 합니다")

    except ValueError:
        return (False, "날짜 형식이 올바르지 않습니다")

    return (True, None)


def validate_card_last4(card_last4: str) -> Tuple[bool, Optional[str]]:
    """카드 마지막 4자리 검증 (하위 호환성)

    Args:
        card_last4: 카드 마지막 4자리

    Returns:
        (검증 성공 여부, 에러 메시지)

    Example:
        >>> validate_card_last4("1234")
        (True, None)
        >>> validate_card_last4("123")
        (False, "카드 마지막 4자리를 입력해주세요")
    """
    # 빈 값은 선택 필드이므로 허용
    if not card_last4 or not card_last4.strip():
        return (True, None)

    # 4자리 숫자 검증
    if not re.match(r'^\d{4}$', card_last4):
        return (False, "카드 마지막 4자리를 입력해주세요 (예: 1234)")

    return (True, None)


def validate_card_number(card_number: str) -> Tuple[bool, Optional[str]]:
    """카드 번호 16자리 검증 (평문)

    Args:
        card_number: 카드 번호 16자리

    Returns:
        (검증 성공 여부, 에러 메시지)

    Example:
        >>> validate_card_number("1234-5678-9012-3456")
        (True, None)
        >>> validate_card_number("1234567890123456")
        (True, None)
        >>> validate_card_number("123")
        (False, "카드 번호는 16자리여야 합니다")
    """
    # 빈 값은 선택 필드이므로 허용
    if not card_number or not card_number.strip():
        return (True, None)

    # 하이픈 제거
    clean = card_number.replace("-", "").replace(" ", "")

    # 16자리 숫자 검증
    if not clean.isdigit():
        return (False, "카드 번호는 숫자만 입력 가능합니다")
    if len(clean) != 16:
        return (False, "카드 번호는 16자리여야 합니다")

    return (True, None)


def validate_card_expiry(expiry: str) -> Tuple[bool, Optional[str]]:
    """카드 유효기간 검증

    Args:
        expiry: 카드 유효기간 (MM/YY 형식)

    Returns:
        (검증 성공 여부, 에러 메시지)

    Example:
        >>> validate_card_expiry("12/26")
        (True, None)
        >>> validate_card_expiry("13/26")
        (False, "유효하지 않은 월입니다 (1~12)")
    """
    # 빈 값은 선택 필드이므로 허용
    if not expiry or not expiry.strip():
        return (True, None)

    # MM/YY 형식 검증
    if not re.match(r'^\d{2}/\d{2}$', expiry):
        return (False, "유효기간 형식이 올바르지 않습니다 (예: 12/26)")

    # 월 검증 (1~12)
    month_str = expiry.split("/")[0]
    try:
        month = int(month_str)
        if month < 1 or month > 12:
            return (False, "유효하지 않은 월입니다 (1~12)")
    except ValueError:
        return (False, "유효기간 형식이 올바르지 않습니다")

    return (True, None)
