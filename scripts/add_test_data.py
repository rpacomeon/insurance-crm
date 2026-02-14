"""
테스트 데이터 추가 스크립트
"""

import sys
from pathlib import Path

# src 디렉토리를 path에 추가
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from database import DatabaseManager
from models import Customer


def add_test_data():
    """테스트 고객 데이터 추가"""
    db = DatabaseManager("data/crm.db")

    # 테스트 고객 데이터
    test_customers = [
        Customer(
            name="홍길동",
            phone="010-1234-5678",
            birth_date="1980-03-15",
            address="서울시 강남구 테헤란로 123",
            email="hong@example.com",
            memo="VIP 고객"
        ),
        Customer(
            name="김철수",
            phone="010-2345-6789",
            birth_date="1975-07-20",
            address="서울시 서초구",
            email="kim@example.com",
            memo="단골 고객"
        ),
        Customer(
            name="이영희",
            phone="010-3456-7890",
            birth_date="1985-11-05",
            address="부산시 해운대구",
            email="lee@example.com"
        ),
        Customer(
            name="박민수",
            phone="010-4567-8901",
            birth_date="1990-01-30",
            address="인천시 남동구"
        ),
        Customer(
            name="정수연",
            phone="010-5678-9012",
            birth_date="1992-06-12",
            address="대전시 유성구",
            email="jung@example.com",
            memo="신규 고객"
        )
    ]

    # 데이터 추가
    for customer in test_customers:
        try:
            customer_id = db.add_customer(customer)
            print(f"[OK] {customer.name} 추가 완료 (ID: {customer_id})")
        except Exception as e:
            print(f"[ERROR] {customer.name} 추가 실패: {e}")

    db.close()
    print("\n테스트 데이터 추가 완료!")


if __name__ == "__main__":
    add_test_data()
