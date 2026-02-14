# -*- coding: utf-8 -*-
"""
보험 계약(Policy) 테스트 - CRUD + 날짜 계산 + 필터 + CASCADE
"""

import sys
import os
import tempfile
import shutil
from pathlib import Path

# src 디렉토리를 sys.path에 추가
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pytest
from database import DatabaseManager
from models import Customer, Policy


@pytest.fixture
def db():
    """테스트용 임시 데이터베이스"""
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, "test_crm.db")
    database = DatabaseManager(db_path)
    yield database
    database.close()
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def sample_customer(db):
    """테스트용 고객 데이터"""
    customer = Customer(
        name="김테스트",
        phone="010-9999-0001",
        resident_id="900101-1234567",
    )
    customer_id = db.add_customer(customer)
    return db.get_customer(customer_id)


@pytest.fixture
def sample_policy(db, sample_customer):
    """테스트용 계약 데이터"""
    policy = Policy(
        customer_id=sample_customer.id,
        insurer="삼성생명",
        product_name="종신보험",
        premium=50000,
        payment_method="card",
        billing_cycle="monthly",
        billing_day=25,
        card_issuer="신한카드",
        card_number="1234-5678-9012-3456",
        card_expiry="12/26",
        contract_start_date="2026-01-01",
    )
    policy_id = db.add_policy(policy)
    return db.get_policy(policy_id)


# =============================================================================
# Policy 모델 테스트
# =============================================================================

def test_policy_creation():
    """Policy 객체 생성 테스트"""
    policy = Policy(
        customer_id=1,
        insurer="삼성생명",
        product_name="종신보험",
        premium=50000,
        payment_method="card",
        billing_cycle="monthly",
        billing_day=25,
        contract_start_date="2026-01-01",
    )

    assert policy.customer_id == 1
    assert policy.insurer == "삼성생명"
    assert policy.product_name == "종신보험"
    assert policy.premium == 50000
    assert policy.payment_method == "card"
    assert policy.billing_cycle == "monthly"
    assert policy.billing_day == 25
    assert policy.status == "active"


def test_policy_to_dict():
    """Policy to_dict() 테스트"""
    policy = Policy(
        customer_id=1,
        insurer="KB손해보험",
        product_name="실손보험",
        premium=30000,
        payment_method="transfer",
        billing_cycle="monthly",
        billing_day=10,
        contract_start_date="2026-02-01",
    )

    d = policy.to_dict()
    assert d["customer_id"] == 1
    assert d["insurer"] == "KB손해보험"
    assert d["premium"] == 30000
    assert d["payment_method"] == "transfer"
    assert d["card_issuer"] is None
    assert d["card_number"] is None


def test_policy_from_db_row():
    """Policy from_db_row() 테스트 (19개 컬럼)"""
    row = (
        1,                       # id
        10,                      # customer_id
        "한화생명",                # insurer
        "연금보험",                # product_name
        100000,                  # premium
        "card",                  # payment_method
        "yearly",                # billing_cycle
        15,                      # billing_day
        "국민카드",                # card_issuer
        "5678-1234-5678-9012",   # card_number
        "06/28",                 # card_expiry
        "2025-01-01",            # contract_start_date
        "2035-01-01",            # contract_end_date
        "active",                # status
        "2026-03-15",            # next_payment_date
        "2026-01-15",            # last_payment_date
        "장기 계약",               # memo
        "2026-01-01 09:00:00",   # created_at
        "2026-02-14 10:00:00",   # updated_at
    )

    policy = Policy.from_db_row(row)

    assert policy.id == 1
    assert policy.customer_id == 10
    assert policy.insurer == "한화생명"
    assert policy.premium == 100000
    assert policy.billing_cycle == "yearly"
    assert policy.billing_day == 15
    assert policy.card_issuer == "국민카드"
    assert policy.card_number == "5678-1234-5678-9012"
    assert policy.card_expiry == "06/28"
    assert policy.contract_end_date == "2035-01-01"
    assert policy.status == "active"
    assert policy.next_payment_date == "2026-03-15"
    assert policy.last_payment_date == "2026-01-15"
    assert policy.memo == "장기 계약"


# =============================================================================
# Policy CRUD 테스트
# =============================================================================

def test_add_policy(db, sample_customer):
    """계약 추가 테스트"""
    policy = Policy(
        customer_id=sample_customer.id,
        insurer="삼성생명",
        product_name="종신보험",
        premium=50000,
        payment_method="card",
        billing_cycle="monthly",
        billing_day=25,
        contract_start_date="2026-01-01",
    )

    policy_id = db.add_policy(policy)
    assert policy_id > 0

    # 저장된 데이터 확인
    saved = db.get_policy(policy_id)
    assert saved is not None
    assert saved.insurer == "삼성생명"
    assert saved.premium == 50000
    assert saved.next_payment_date != ""  # 자동 계산됨


def test_get_policy(db, sample_policy):
    """계약 단건 조회 테스트"""
    policy = db.get_policy(sample_policy.id)
    assert policy is not None
    assert policy.id == sample_policy.id
    assert policy.insurer == "삼성생명"


def test_get_policy_not_found(db):
    """존재하지 않는 계약 조회"""
    assert db.get_policy(99999) is None


def test_get_policies_by_customer(db, sample_customer):
    """고객별 계약 목록 조회 테스트"""
    # 2개 계약 추가
    for name in ["종신보험", "실손보험"]:
        policy = Policy(
            customer_id=sample_customer.id,
            insurer="삼성생명",
            product_name=name,
            premium=50000,
            payment_method="card",
            billing_cycle="monthly",
            billing_day=25,
            contract_start_date="2026-01-01",
        )
        db.add_policy(policy)

    policies = db.get_policies_by_customer(sample_customer.id)
    assert len(policies) == 2


def test_get_policies_empty(db, sample_customer):
    """계약 없는 고객 조회 시 빈 리스트"""
    policies = db.get_policies_by_customer(sample_customer.id)
    assert policies == []


def test_update_policy(db, sample_policy):
    """계약 수정 테스트"""
    sample_policy.premium = 60000
    sample_policy.billing_day = 10

    result = db.update_policy(sample_policy)
    assert result is True

    updated = db.get_policy(sample_policy.id)
    assert updated.premium == 60000
    assert updated.billing_day == 10


def test_delete_policy(db, sample_policy):
    """계약 삭제 테스트"""
    result = db.delete_policy(sample_policy.id)
    assert result is True

    deleted = db.get_policy(sample_policy.id)
    assert deleted is None


def test_delete_policy_not_found(db):
    """존재하지 않는 계약 삭제"""
    result = db.delete_policy(99999)
    assert result is False


# =============================================================================
# CASCADE 삭제 테스트
# =============================================================================

def test_cascade_delete(db, sample_customer):
    """고객 삭제 시 관련 계약도 CASCADE 삭제"""
    # 계약 2개 추가
    for name in ["종신보험", "실손보험"]:
        policy = Policy(
            customer_id=sample_customer.id,
            insurer="삼성생명",
            product_name=name,
            premium=50000,
            payment_method="card",
            billing_cycle="monthly",
            billing_day=25,
            contract_start_date="2026-01-01",
        )
        db.add_policy(policy)

    # 계약 확인
    policies = db.get_policies_by_customer(sample_customer.id)
    assert len(policies) == 2

    # 고객 삭제
    db.delete_customer(sample_customer.id)

    # CASCADE 확인 → 계약도 삭제됨
    policies = db.get_policies_by_customer(sample_customer.id)
    assert len(policies) == 0


# =============================================================================
# 날짜 계산 테스트
# =============================================================================

def test_calculate_next_payment_monthly(db):
    """월납 다음 납부일 계산"""
    result = db.calculate_next_payment_date("2026-01-15", "monthly", 25)
    assert result == "2026-02-25"


def test_calculate_next_payment_yearly(db):
    """연납 다음 납부일 계산"""
    result = db.calculate_next_payment_date("2026-01-01", "yearly", 15)
    assert result == "2027-01-15"


def test_calculate_next_payment_month_end(db):
    """월말 처리 테스트 (31일 → 2월 28일)"""
    result = db.calculate_next_payment_date("2026-01-31", "monthly", 31)
    assert result == "2026-02-28"


def test_calculate_next_payment_leap_year(db):
    """윤년 테스트 (2028년 2월 29일)"""
    result = db.calculate_next_payment_date("2028-01-31", "monthly", 31)
    assert result == "2028-02-29"


def test_calculate_next_payment_day_30_in_feb(db):
    """30일 납부일의 2월 처리"""
    result = db.calculate_next_payment_date("2026-01-30", "monthly", 30)
    assert result == "2026-02-28"


# =============================================================================
# mark_payment_completed 테스트
# =============================================================================

def test_mark_payment_completed(db, sample_policy):
    """납부 완료 처리 테스트"""
    old_next = sample_policy.next_payment_date

    result = db.mark_payment_completed(sample_policy.id, "2026-02-25")
    assert result is True

    updated = db.get_policy(sample_policy.id)
    assert updated.last_payment_date == "2026-02-25"
    assert updated.next_payment_date != old_next  # 다음 날짜로 변경됨
    assert updated.status == "active"


def test_mark_payment_completed_not_found(db):
    """존재하지 않는 계약 납부 완료"""
    result = db.mark_payment_completed(99999, "2026-02-25")
    assert result is False


# =============================================================================
# 필터 조회 테스트
# =============================================================================

def test_get_upcoming_payments(db, sample_customer):
    """납부 임박 계약 조회"""
    from datetime import datetime, timedelta

    # 3일 후 납부 예정 계약 생성
    target_date = (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d")
    target_day = int(target_date.split("-")[2])

    policy = Policy(
        customer_id=sample_customer.id,
        insurer="삼성생명",
        product_name="종신보험",
        premium=50000,
        payment_method="card",
        billing_cycle="monthly",
        billing_day=target_day,
        contract_start_date="2026-01-01",
        next_payment_date=target_date,  # 직접 설정
    )
    db.add_policy(policy)

    # 7일 이내 납부 임박 조회
    results = db.get_upcoming_payments(days_ahead=7)
    assert len(results) >= 1

    # 반환 구조 확인
    item = results[0]
    assert "policy" in item
    assert "customer" in item
    assert "days_left" in item
    assert item["days_left"] >= 0


def test_get_overdue_policies(db, sample_customer):
    """연체 계약 조회 (카드결제만 대상)"""
    # 과거 날짜의 카드결제 계약 생성 (연체 시뮬레이션)
    policy = Policy(
        customer_id=sample_customer.id,
        insurer="삼성생명",
        product_name="연체보험",
        premium=50000,
        payment_method="card",
        billing_cycle="monthly",
        billing_day=1,
        contract_start_date="2025-01-01",
        next_payment_date="2025-12-01",  # 과거 날짜
        status="active",
    )
    db.add_policy(policy)

    # 자동 갱신으로 overdue 상태로 변경 (카드결제만)
    db.auto_update_payment_status()

    results = db.get_overdue_policies()
    assert len(results) >= 1

    item = results[0]
    assert "policy" in item
    assert "customer" in item
    assert "overdue_days" in item
    assert item["overdue_days"] > 0


def test_transfer_not_marked_overdue(db, sample_customer):
    """계좌이체 계약은 연체 처리 안 됨"""
    policy = Policy(
        customer_id=sample_customer.id,
        insurer="삼성생명",
        product_name="이체보험",
        premium=30000,
        payment_method="transfer",
        billing_cycle="monthly",
        billing_day=1,
        contract_start_date="2025-01-01",
        next_payment_date="2025-12-01",  # 과거 날짜
        status="active",
    )
    policy_id = db.add_policy(policy)

    # 자동 갱신 실행 → 계좌이체는 무시
    db.auto_update_payment_status()

    # 계좌이체 계약은 여전히 active 상태
    saved = db.get_policy(policy_id)
    assert saved.status == "active"

    # 연체 목록에도 나타나지 않음
    results = db.get_overdue_policies()
    transfer_overdue = [r for r in results if r["policy"].id == policy_id]
    assert len(transfer_overdue) == 0


# =============================================================================
# 카드/계좌이체 분기 테스트
# =============================================================================

def test_policy_card_payment(db, sample_customer):
    """카드 결제 계약: 카드 정보 저장"""
    policy = Policy(
        customer_id=sample_customer.id,
        insurer="삼성생명",
        product_name="종신보험",
        premium=50000,
        payment_method="card",
        billing_cycle="monthly",
        billing_day=25,
        card_issuer="신한카드",
        card_number="4321-5678-9012-3456",
        card_expiry="06/28",
        contract_start_date="2026-01-01",
    )
    policy_id = db.add_policy(policy)
    saved = db.get_policy(policy_id)

    assert saved.payment_method == "card"
    assert saved.card_issuer == "신한카드"
    assert saved.card_number == "4321-5678-9012-3456"
    assert saved.card_expiry == "06/28"


def test_policy_transfer_payment(db, sample_customer):
    """계좌이체 계약: 카드 정보 없음"""
    policy = Policy(
        customer_id=sample_customer.id,
        insurer="KB손해보험",
        product_name="실손보험",
        premium=30000,
        payment_method="transfer",
        billing_cycle="monthly",
        billing_day=10,
        contract_start_date="2026-02-01",
    )
    policy_id = db.add_policy(policy)
    saved = db.get_policy(policy_id)

    assert saved.payment_method == "transfer"
    assert saved.card_issuer is None
    assert saved.card_number is None
    assert saved.card_expiry is None


# =============================================================================
# 한글 인코딩 테스트 (AP-004)
# =============================================================================

def test_korean_encoding_policy(db, sample_customer):
    """계약 데이터 한글 저장/조회 (AP-004 대응)"""
    policy = Policy(
        customer_id=sample_customer.id,
        insurer="삼성생명",
        product_name="(무)종신보험 프리미엄",
        premium=50000,
        payment_method="card",
        billing_cycle="monthly",
        billing_day=25,
        card_issuer="신한카드",
        contract_start_date="2026-01-01",
        memo="특약 포함: 암진단금 3천만원",
    )
    policy_id = db.add_policy(policy)
    saved = db.get_policy(policy_id)

    assert saved.product_name == "(무)종신보험 프리미엄"
    assert saved.memo == "특약 포함: 암진단금 3천만원"
