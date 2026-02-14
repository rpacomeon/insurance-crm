# -*- coding: utf-8 -*-
"""
데이터베이스 계층 - SQLite CRUD 작업
"""

import sqlite3
from pathlib import Path
from typing import List, Optional

from models import Customer


class DatabaseManager:
    """SQLite 데이터베이스 관리 클래스"""

    def __init__(self, db_path: str = "data/crm.db"):
        """DatabaseManager 초기화

        Args:
            db_path: 데이터베이스 파일 경로
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = None
        self._connect()
        self._create_tables()

    def _connect(self) -> None:
        """데이터베이스 연결 및 UTF-8 인코딩 설정 (AP-004 대응)"""
        self.connection = sqlite3.connect(str(self.db_path))
        self.connection.execute("PRAGMA encoding = 'UTF-8'")
        self.connection.row_factory = sqlite3.Row

    def _create_tables(self) -> None:
        """customers 테이블 생성 (없는 경우) 및 기존 테이블 마이그레이션"""
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL UNIQUE,
            resident_id TEXT DEFAULT '',
            birth_date TEXT,
            address TEXT,
            email TEXT,
            memo TEXT,
            occupation TEXT,
            driving_type TEXT DEFAULT 'none',
            commercial_detail TEXT,
            payment_method TEXT,
            med_medication TEXT,
            med_hospitalized INTEGER DEFAULT 0,
            med_hospital_detail TEXT,
            med_recent_exam INTEGER DEFAULT 0,
            med_recent_exam_detail TEXT,
            med_5yr_diagnosis TEXT,
            med_5yr_custom TEXT,
            notification_content TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        """

        create_indexes_sql = [
            "CREATE INDEX IF NOT EXISTS idx_customer_name ON customers(name);",
            "CREATE INDEX IF NOT EXISTS idx_customer_phone ON customers(phone);",
        ]

        cursor = self.connection.cursor()
        cursor.execute(create_table_sql)

        for index_sql in create_indexes_sql:
            cursor.execute(index_sql)

        # 기존 테이블 마이그레이션 (새 컬럼 추가)
        self._migrate_existing_tables(cursor)

        self.connection.commit()

    def _migrate_existing_tables(self, cursor) -> None:
        """기존 테이블에 새 컬럼 추가 (있으면 무시)"""
        # 현재 테이블 컬럼 목록 조회
        cursor.execute("PRAGMA table_info(customers)")
        existing_columns = {row[1] for row in cursor.fetchall()}

        # 추가할 컬럼 정의
        new_columns = [
            ("resident_id", "TEXT DEFAULT ''"),
            ("occupation", "TEXT"),
            ("driving_type", "TEXT DEFAULT 'none'"),
            ("commercial_detail", "TEXT"),
            ("payment_method", "TEXT"),
            ("med_medication", "TEXT"),
            ("med_hospitalized", "INTEGER DEFAULT 0"),
            ("med_hospital_detail", "TEXT"),
            ("med_recent_exam", "INTEGER DEFAULT 0"),
            ("med_recent_exam_detail", "TEXT"),
            ("med_5yr_diagnosis", "TEXT"),
            ("med_5yr_custom", "TEXT"),
            ("notification_content", "TEXT"),
        ]

        # 누락된 컬럼 추가
        for col_name, col_type in new_columns:
            if col_name not in existing_columns:
                alter_sql = f"ALTER TABLE customers ADD COLUMN {col_name} {col_type}"
                cursor.execute(alter_sql)

    def add_customer(self, customer: Customer) -> int:
        """새 고객 추가

        Args:
            customer: 추가할 고객 정보

        Returns:
            생성된 고객 ID

        Raises:
            sqlite3.IntegrityError: 전화번호 중복 시
        """
        timestamp = Customer.get_current_timestamp()

        cursor = self.connection.cursor()
        cursor.execute(
            """
            INSERT INTO customers (
                name, phone, resident_id, birth_date, address, email, memo, occupation,
                driving_type, commercial_detail, payment_method,
                med_medication, med_hospitalized, med_hospital_detail,
                med_recent_exam, med_recent_exam_detail, med_5yr_diagnosis, med_5yr_custom,
                notification_content, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                customer.name,
                customer.phone,
                customer.resident_id,
                customer.birth_date,
                customer.address,
                customer.email,
                customer.memo,
                customer.occupation,
                customer.driving_type,
                customer.commercial_detail,
                customer.payment_method,
                customer.med_medication,
                1 if customer.med_hospitalized else 0,
                customer.med_hospital_detail,
                1 if customer.med_recent_exam else 0,
                customer.med_recent_exam_detail,
                customer.med_5yr_diagnosis,
                customer.med_5yr_custom,
                customer.notification_content,
                timestamp,
                timestamp,
            ),
        )
        self.connection.commit()
        return cursor.lastrowid

    def get_customer(self, customer_id: int) -> Optional[Customer]:
        """ID로 고객 조회

        Args:
            customer_id: 고객 ID

        Returns:
            Customer 객체 또는 None (없는 경우)
        """
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM customers WHERE id = ?", (customer_id,))
        row = cursor.fetchone()

        if row:
            return Customer.from_db_row(tuple(row))
        return None

    def get_all_customers(self) -> List[Customer]:
        """모든 고객 조회

        Returns:
            Customer 객체 리스트
        """
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM customers ORDER BY name ASC")
        rows = cursor.fetchall()

        return [Customer.from_db_row(tuple(row)) for row in rows]

    def search_customers(self, keyword: str) -> List[Customer]:
        """이름 또는 전화번호로 고객 검색

        Args:
            keyword: 검색 키워드

        Returns:
            검색 결과 Customer 객체 리스트
        """
        cursor = self.connection.cursor()
        search_pattern = f"%{keyword}%"

        cursor.execute(
            """
            SELECT * FROM customers
            WHERE name LIKE ? OR phone LIKE ?
            ORDER BY name ASC
            """,
            (search_pattern, search_pattern),
        )
        rows = cursor.fetchall()

        return [Customer.from_db_row(tuple(row)) for row in rows]

    def update_customer(self, customer: Customer) -> bool:
        """고객 정보 수정

        Args:
            customer: 수정할 고객 정보 (id 필수)

        Returns:
            성공 여부
        """
        if customer.id is None:
            return False

        timestamp = Customer.get_current_timestamp()

        cursor = self.connection.cursor()
        cursor.execute(
            """
            UPDATE customers
            SET name = ?, phone = ?, resident_id = ?, birth_date = ?, address = ?, email = ?, memo = ?, occupation = ?,
                driving_type = ?, commercial_detail = ?, payment_method = ?,
                med_medication = ?, med_hospitalized = ?, med_hospital_detail = ?,
                med_recent_exam = ?, med_recent_exam_detail = ?, med_5yr_diagnosis = ?, med_5yr_custom = ?,
                notification_content = ?, updated_at = ?
            WHERE id = ?
            """,
            (
                customer.name,
                customer.phone,
                customer.resident_id,
                customer.birth_date,
                customer.address,
                customer.email,
                customer.memo,
                customer.occupation,
                customer.driving_type,
                customer.commercial_detail,
                customer.payment_method,
                customer.med_medication,
                1 if customer.med_hospitalized else 0,
                customer.med_hospital_detail,
                1 if customer.med_recent_exam else 0,
                customer.med_recent_exam_detail,
                customer.med_5yr_diagnosis,
                customer.med_5yr_custom,
                customer.notification_content,
                timestamp,
                customer.id,
            ),
        )
        self.connection.commit()
        return cursor.rowcount > 0

    def delete_customer(self, customer_id: int) -> bool:
        """고객 삭제

        Args:
            customer_id: 삭제할 고객 ID

        Returns:
            성공 여부
        """
        cursor = self.connection.cursor()
        cursor.execute("DELETE FROM customers WHERE id = ?", (customer_id,))
        self.connection.commit()
        return cursor.rowcount > 0

    def close(self) -> None:
        """데이터베이스 연결 종료 (AP-007 대응)"""
        if self.connection:
            self.connection.close()
            self.connection = None

    def __del__(self):
        """소멸자 - 연결 자동 종료"""
        self.close()
