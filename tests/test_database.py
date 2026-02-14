"""
Tests for database.py
"""

import sys
import sqlite3
import tempfile
from pathlib import Path

# src 디렉토리를 path에 추가
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from models import Customer
from database import DatabaseManager


def test_database_creation():
    """데이터베이스 생성 테스트"""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        db = DatabaseManager(str(db_path))

        assert db_path.exists()
        db.close()


def test_add_customer():
    """고객 추가 테스트"""
    with tempfile.TemporaryDirectory() as tmpdir:
        db = DatabaseManager(str(Path(tmpdir) / "test.db"))

        customer = Customer(
            name="테스트고객",
            phone="010-0000-0000",
            birth_date="1990-01-01"
        )

        customer_id = db.add_customer(customer)

        assert customer_id > 0
        db.close()


def test_get_customer():
    """고객 조회 테스트"""
    with tempfile.TemporaryDirectory() as tmpdir:
        db = DatabaseManager(str(Path(tmpdir) / "test.db"))

        # 고객 추가
        customer = Customer(name="조회테스트", phone="010-1111-1111")
        customer_id = db.add_customer(customer)

        # 조회
        retrieved = db.get_customer(customer_id)

        assert retrieved is not None
        assert retrieved.name == "조회테스트"
        assert retrieved.phone == "010-1111-1111"
        db.close()


def test_get_all_customers():
    """모든 고객 조회 테스트"""
    with tempfile.TemporaryDirectory() as tmpdir:
        db = DatabaseManager(str(Path(tmpdir) / "test.db"))

        # 여러 고객 추가
        db.add_customer(Customer(name="고객1", phone="010-1111-0000"))
        db.add_customer(Customer(name="고객2", phone="010-2222-0000"))
        db.add_customer(Customer(name="고객3", phone="010-3333-0000"))

        # 전체 조회
        customers = db.get_all_customers()

        assert len(customers) == 3
        assert all(isinstance(c, Customer) for c in customers)
        db.close()


def test_search_customers():
    """고객 검색 테스트"""
    with tempfile.TemporaryDirectory() as tmpdir:
        db = DatabaseManager(str(Path(tmpdir) / "test.db"))

        # 테스트 데이터 추가
        db.add_customer(Customer(name="홍길동", phone="010-1234-5678"))
        db.add_customer(Customer(name="김철수", phone="010-9999-8888"))
        db.add_customer(Customer(name="홍명보", phone="010-1111-2222"))

        # 이름으로 검색
        results = db.search_customers("홍")
        assert len(results) == 2

        # 전화번호로 검색
        results = db.search_customers("1234")
        assert len(results) == 1
        assert results[0].name == "홍길동"

        db.close()


def test_update_customer():
    """고객 정보 수정 테스트"""
    with tempfile.TemporaryDirectory() as tmpdir:
        db = DatabaseManager(str(Path(tmpdir) / "test.db"))

        # 고객 추가
        customer = Customer(name="수정전", phone="010-0000-0000")
        customer_id = db.add_customer(customer)

        # 수정
        customer_to_update = db.get_customer(customer_id)
        customer_to_update.name = "수정후"
        customer_to_update.phone = "010-9999-9999"

        success = db.update_customer(customer_to_update)
        assert success

        # 수정 확인
        updated = db.get_customer(customer_id)
        assert updated.name == "수정후"
        assert updated.phone == "010-9999-9999"

        db.close()


def test_delete_customer():
    """고객 삭제 테스트"""
    with tempfile.TemporaryDirectory() as tmpdir:
        db = DatabaseManager(str(Path(tmpdir) / "test.db"))

        # 고객 추가
        customer = Customer(name="삭제대상", phone="010-0000-0000")
        customer_id = db.add_customer(customer)

        # 삭제
        success = db.delete_customer(customer_id)
        assert success

        # 삭제 확인
        deleted = db.get_customer(customer_id)
        assert deleted is None

        db.close()


def test_duplicate_phone():
    """중복 전화번호 입력 시 에러 테스트"""
    with tempfile.TemporaryDirectory() as tmpdir:
        db = DatabaseManager(str(Path(tmpdir) / "test.db"))

        # 첫 번째 고객 추가
        db.add_customer(Customer(name="고객1", phone="010-1234-5678"))

        # 같은 전화번호로 두 번째 고객 추가 시도
        try:
            db.add_customer(Customer(name="고객2", phone="010-1234-5678"))
            assert False, "중복 전화번호 에러가 발생해야 함"
        except sqlite3.IntegrityError:
            pass  # 예상된 에러

        db.close()


def test_korean_encoding():
    """한글 인코딩 테스트 (AP-004)"""
    with tempfile.TemporaryDirectory() as tmpdir:
        db = DatabaseManager(str(Path(tmpdir) / "test.db"))

        # 한글 데이터 추가
        customer = Customer(
            name="홍길동",
            phone="010-1234-5678",
            address="서울시 강남구 테헤란로 123",
            memo="중요 고객입니다."
        )

        customer_id = db.add_customer(customer)

        # 조회 및 확인
        retrieved = db.get_customer(customer_id)
        assert retrieved.name == "홍길동"
        assert retrieved.address == "서울시 강남구 테헤란로 123"
        assert retrieved.memo == "중요 고객입니다."

        db.close()
