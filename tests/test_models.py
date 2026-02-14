"""
Tests for models.py
"""

import sys
from pathlib import Path

# src 디렉토리를 path에 추가
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from models import Customer


def test_customer_creation():
    """Customer 객체 생성 테스트 (기본 정보)"""
    customer = Customer(
        name="홍길동",
        phone="010-1234-5678",
        resident_id="900115-1234567",
        address="서울시 강남구",
        memo="VIP 고객"
    )

    assert customer.name == "홍길동"
    assert customer.phone == "010-1234-5678"
    assert customer.resident_id == "900115-1234567"


def test_customer_with_insurance_info():
    """보험 정보 포함 Customer 생성 테스트"""
    customer = Customer(
        name="김철수",
        phone="010-9999-8888",
        resident_id="800315-2345678",
        driving_type="commercial",
        commercial_detail="taxi,construction",
        payment_method="계좌이체"
    )

    assert customer.driving_type == "commercial"
    assert customer.commercial_detail == "taxi,construction"
    assert customer.payment_method == "계좌이체"


def test_customer_with_medical_info():
    """건강 정보 포함 Customer 생성 테스트"""
    customer = Customer(
        name="이영희",
        phone="010-1111-2222",
        resident_id="750720-1234567",
        med_medication="고혈압,당뇨병",
        med_hospitalized=True,
        med_hospital_detail="2024년 무릎 수술",
        med_5yr_diagnosis="암"
    )

    assert customer.med_medication == "고혈압,당뇨병"
    assert customer.med_hospitalized is True
    assert customer.med_hospital_detail == "2024년 무릎 수술"
    assert customer.med_5yr_diagnosis == "암"


def test_customer_to_dict():
    """Customer to_dict() 메서드 테스트"""
    customer = Customer(
        id=1,
        name="김철수",
        phone="010-9999-8888",
        resident_id="800315-1234567",
        driving_type="personal",
        payment_method="신용카드",
        med_medication="고혈압",
        med_hospitalized=False,
        notification_content="고혈압 복용 중",
        created_at="2026-02-14 10:00:00",
        updated_at="2026-02-14 10:00:00"
    )

    data = customer.to_dict()

    assert data['id'] == 1
    assert data['name'] == "김철수"
    assert data['phone'] == "010-9999-8888"
    assert data['resident_id'] == "800315-1234567"
    assert data['driving_type'] == "personal"
    assert data['payment_method'] == "신용카드"
    assert data['med_medication'] == "고혈압"
    assert data['med_hospitalized'] is False
    assert data['notification_content'] == "고혈압 복용 중"
    assert 'created_at' in data
    assert 'updated_at' in data


def test_customer_from_db_row():
    """Customer from_db_row() 메서드 테스트 (확장 필드 포함)"""
    # DB row 시뮬레이션 (22개 컬럼 - 전체 스키마)
    row = (
        1,                       # id
        "이영희",                  # name
        "010-1111-2222",          # phone
        "750720-1234567",         # resident_id
        None,                    # birth_date
        "부산시 해운대구",           # address
        None,                    # email
        "단골 고객",               # memo
        "자영업",                  # occupation
        "personal",              # driving_type
        None,                    # commercial_detail
        "자동이체",                # payment_method
        "고혈압,당뇨병",           # med_medication
        1,                       # med_hospitalized (INTEGER)
        "2024년 무릎 수술",        # med_hospital_detail
        0,                       # med_recent_exam (INTEGER)
        None,                    # med_recent_exam_detail
        "암",                    # med_5yr_diagnosis
        None,                    # med_5yr_custom
        "고혈압 당뇨 고지",        # notification_content
        "2026-02-14 10:00:00",   # created_at
        "2026-02-14 10:00:00"    # updated_at
    )

    customer = Customer.from_db_row(row)

    assert customer.id == 1
    assert customer.name == "이영희"
    assert customer.phone == "010-1111-2222"
    assert customer.resident_id == "750720-1234567"
    assert customer.address == "부산시 해운대구"
    assert customer.occupation == "자영업"
    assert customer.driving_type == "personal"
    assert customer.payment_method == "자동이체"
    assert customer.med_medication == "고혈압,당뇨병"
    assert customer.med_hospitalized is True  # INTEGER 1 → True 변환
    assert customer.med_hospital_detail == "2024년 무릎 수술"
    assert customer.med_recent_exam is False  # INTEGER 0 → False
    assert customer.med_5yr_diagnosis == "암"
    assert customer.med_5yr_custom is None
    assert customer.notification_content == "고혈압 당뇨 고지"


def test_customer_optional_fields():
    """선택 필드가 None인 경우 테스트"""
    customer = Customer(
        name="박민수",
        phone="010-3333-4444",
        resident_id="850101-1234567"
    )

    assert customer.address is None
    assert customer.email is None
    assert customer.memo is None
    assert customer.commercial_detail is None
    assert customer.payment_method is None
    assert customer.med_medication is None
    assert customer.med_hospitalized is False
    assert customer.med_hospital_detail is None
    assert customer.med_5yr_diagnosis is None
    assert customer.notification_content is None


def test_customer_default_values():
    """기본값 테스트"""
    customer = Customer(
        name="최영수",
        phone="010-5555-6666",
        resident_id="950505-1234567"
    )

    assert customer.resident_id == "950505-1234567"
    assert customer.driving_type == "none"  # 기본값
    assert customer.med_hospitalized is False  # 기본값


def test_get_current_timestamp():
    """현재 시간 문자열 생성 테스트"""
    timestamp = Customer.get_current_timestamp()

    assert isinstance(timestamp, str)
    assert len(timestamp) == 19  # "YYYY-MM-DD HH:MM:SS" 형식
    assert timestamp[4] == "-"
    assert timestamp[7] == "-"
    assert timestamp[10] == " "
    assert timestamp[13] == ":"
    assert timestamp[16] == ":"
