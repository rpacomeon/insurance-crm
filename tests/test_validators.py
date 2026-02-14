"""
Tests for validators.py
"""

import sys
from pathlib import Path

# src 디렉토리를 path에 추가
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils.validators import (
    validate_phone,
    validate_email,
    validate_birth_date,
    validate_name,
    validate_resident_id,
)


# 전화번호 검증 테스트
def test_validate_phone_valid():
    """올바른 전화번호 테스트"""
    assert validate_phone("010-1234-5678")[0] == True
    assert validate_phone("01012345678")[0] == True
    assert validate_phone("02-1234-5678")[0] == True
    assert validate_phone("031-123-4567")[0] == True


def test_validate_phone_invalid():
    """잘못된 전화번호 테스트"""
    assert validate_phone("")[0] == False
    assert validate_phone("   ")[0] == False
    assert validate_phone("123")[0] == False
    assert validate_phone("abc-defg-hijk")[0] == False
    assert validate_phone("010-12-34")[0] == False


# 이메일 검증 테스트
def test_validate_email_valid():
    """올바른 이메일 테스트"""
    assert validate_email("test@example.com")[0] == True
    assert validate_email("user.name@company.co.kr")[0] == True
    assert validate_email("admin@test.org")[0] == True
    assert validate_email("")[0] == True  # 선택 필드이므로 빈 값 허용
    assert validate_email("   ")[0] == True


def test_validate_email_invalid():
    """잘못된 이메일 테스트"""
    assert validate_email("invalid")[0] == False
    assert validate_email("@example.com")[0] == False
    assert validate_email("test@")[0] == False
    assert validate_email("test @example.com")[0] == False


# 생년월일 검증 테스트
def test_validate_birth_date_valid():
    """올바른 생년월일 테스트"""
    assert validate_birth_date("1990-01-15")[0] == True
    assert validate_birth_date("2000-12-31")[0] == True
    assert validate_birth_date("1985-05-20")[0] == True
    assert validate_birth_date("")[0] == True  # 선택 필드이므로 빈 값 허용
    assert validate_birth_date("   ")[0] == True


def test_validate_birth_date_invalid():
    """잘못된 생년월일 테스트"""
    assert validate_birth_date("2023-13-01")[0] == False  # 13월
    assert validate_birth_date("2023-01-32")[0] == False  # 32일
    assert validate_birth_date("1990/01/15")[0] == False  # 형식 오류
    assert validate_birth_date("90-01-15")[0] == False    # 연도 2자리
    assert validate_birth_date("invalid")[0] == False


# 이름 검증 테스트
def test_validate_name_valid():
    """올바른 이름 테스트"""
    assert validate_name("홍길동")[0] == True
    assert validate_name("김철수")[0] == True
    assert validate_name("이")[0] == True  # 1글자도 허용


def test_validate_name_invalid():
    """잘못된 이름 테스트"""
    assert validate_name("")[0] == False
    assert validate_name("   ")[0] == False


# 주민등록번호 검증 테스트
def test_validate_resident_id_valid():
    """올바른 주민등록번호 테스트"""
    assert validate_resident_id("900115-1234567")[0] == True
    assert validate_resident_id("800315-2345678")[0] == True
    assert validate_resident_id("750720-1111111")[0] == True


def test_validate_resident_id_invalid():
    """잘못된 주민등록번호 테스트"""
    assert validate_resident_id("")[0] == False  # 빈 값
    assert validate_resident_id("   ")[0] == False  # 공백
    assert validate_resident_id("900115")[0] == False  # 앞 6자리만
    assert validate_resident_id("9001151234567")[0] == False  # 하이픈 없음
    assert validate_resident_id("90-01-15-1234567")[0] == False  # 형식 오류
    assert validate_resident_id("900115-123456")[0] == False  # 뒤 6자리만
    assert validate_resident_id("900115-12345678")[0] == False  # 뒤 8자리
    assert validate_resident_id("abcdef-1234567")[0] == False  # 문자 포함


# 에러 메시지 테스트
def test_error_messages():
    """에러 메시지 반환 확인"""
    success, error = validate_phone("")
    assert success == False
    assert error is not None
    assert "필수" in error

    success, error = validate_email("invalid")
    assert success == False
    assert error is not None
    assert "형식" in error

    success, error = validate_name("")
    assert success == False
    assert error is not None

    success, error = validate_resident_id("")
    assert success == False
    assert error is not None
    assert "필수" in error

    success, error = validate_resident_id("invalid")
    assert success == False
    assert error is not None
    assert "형식" in error
