# -*- coding: utf-8 -*-
"""
데이터베이스 계층 - SQLite CRUD 작업
"""

import sqlite3
from pathlib import Path
from typing import List, Optional, Dict
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from models import Customer, Policy


class DatabaseManager:
    """SQLite 데이터베이스 관리 클래스"""

    # 명시적 컬럼 목록 (from_db_row 순서와 일치해야 함)
    # ALTER TABLE로 추가된 컬럼은 테이블 끝에 배치되므로
    # SELECT * 대신 이 목록을 사용하여 순서를 보장한다.
    CUSTOMER_COLUMNS = (
        "id, name, phone, resident_id, birth_date, address, email, memo, "
        "occupation, driving_type, commercial_detail, payment_method, "
        "med_medication, med_hospitalized, med_hospital_detail, "
        "med_recent_exam, med_recent_exam_detail, med_5yr_diagnosis, med_5yr_custom, "
        "notification_content, created_at, updated_at"
    )

    POLICY_COLUMNS = (
        "id, customer_id, insurer, product_name, premium, "
        "payment_method, billing_cycle, billing_day, "
        "card_issuer, card_number, card_expiry, "
        "contract_start_date, contract_end_date, "
        "status, next_payment_date, last_payment_date, "
        "memo, created_at, updated_at"
    )

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
        self.connection.execute("PRAGMA foreign_keys = ON")
        self.connection.row_factory = sqlite3.Row

    def _create_tables(self) -> None:
        """customers, policies 테이블 생성 (없는 경우) 및 기존 테이블 마이그레이션"""
        create_customers_table_sql = """
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

        create_policies_table_sql = """
        CREATE TABLE IF NOT EXISTS policies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER NOT NULL,

            -- 계약 정보
            insurer TEXT NOT NULL,
            product_name TEXT NOT NULL,
            premium INTEGER NOT NULL,

            -- 결제 정보
            payment_method TEXT NOT NULL,
            billing_cycle TEXT NOT NULL,
            billing_day INTEGER NOT NULL,

            -- 카드 정보 (Phase 6-2: 전체 16자리)
            card_issuer TEXT,
            card_number TEXT,
            card_expiry TEXT,

            -- 계약 기간
            contract_start_date TEXT NOT NULL,
            contract_end_date TEXT,

            -- 상태 관리
            status TEXT DEFAULT 'active',
            next_payment_date TEXT NOT NULL,
            last_payment_date TEXT,

            memo TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,

            FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE
        );
        """

        create_indexes_sql = [
            # Customer 인덱스
            "CREATE INDEX IF NOT EXISTS idx_customer_name ON customers(name);",
            "CREATE INDEX IF NOT EXISTS idx_customer_phone ON customers(phone);",
            # Policy 인덱스
            "CREATE INDEX IF NOT EXISTS idx_policy_customer ON policies(customer_id);",
            "CREATE INDEX IF NOT EXISTS idx_policy_next_payment ON policies(next_payment_date);",
            "CREATE INDEX IF NOT EXISTS idx_policy_status ON policies(status);",
        ]

        cursor = self.connection.cursor()
        cursor.execute(create_customers_table_sql)
        cursor.execute(create_policies_table_sql)

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

        # card_last4 → card_number 마이그레이션
        self._migrate_card_field(cursor)

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
        cursor.execute(f"SELECT {self.CUSTOMER_COLUMNS} FROM customers WHERE id = ?", (customer_id,))
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
        cursor.execute(f"SELECT {self.CUSTOMER_COLUMNS} FROM customers ORDER BY name ASC")
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
            f"""
            SELECT {self.CUSTOMER_COLUMNS} FROM customers
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

    # =============================================================================
    # Policy 관련 메서드
    # =============================================================================

    def add_policy(self, policy: Policy) -> int:
        """새 보험 계약 추가

        Args:
            policy: 추가할 계약 정보

        Returns:
            생성된 계약 ID
        """
        timestamp = Policy.get_current_timestamp()

        # next_payment_date가 없으면 자동 계산
        if not policy.next_payment_date:
            policy.next_payment_date = self.calculate_next_payment_date(
                policy.contract_start_date,
                policy.billing_cycle,
                policy.billing_day
            )

        cursor = self.connection.cursor()
        cursor.execute(
            """
            INSERT INTO policies (
                customer_id, insurer, product_name, premium,
                payment_method, billing_cycle, billing_day,
                card_issuer, card_number, card_expiry,
                contract_start_date, contract_end_date,
                status, next_payment_date, last_payment_date,
                memo, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                policy.customer_id,
                policy.insurer,
                policy.product_name,
                policy.premium,
                policy.payment_method,
                policy.billing_cycle,
                policy.billing_day,
                policy.card_issuer,
                policy.card_number,
                policy.card_expiry,
                policy.contract_start_date,
                policy.contract_end_date,
                policy.status,
                policy.next_payment_date,
                policy.last_payment_date,
                policy.memo,
                timestamp,
                timestamp,
            ),
        )
        self.connection.commit()
        return cursor.lastrowid

    def get_policy(self, policy_id: int) -> Optional[Policy]:
        """ID로 계약 조회

        Args:
            policy_id: 계약 ID

        Returns:
            Policy 객체 또는 None (없는 경우)
        """
        cursor = self.connection.cursor()
        cursor.execute(f"SELECT {self.POLICY_COLUMNS} FROM policies WHERE id = ?", (policy_id,))
        row = cursor.fetchone()

        if row:
            return Policy.from_db_row(tuple(row))
        return None

    def get_policies_by_customer(self, customer_id: int) -> List[Policy]:
        """고객 ID로 계약 목록 조회

        Args:
            customer_id: 고객 ID

        Returns:
            Policy 객체 리스트 (생성일 역순)
        """
        cursor = self.connection.cursor()
        cursor.execute(
            f"SELECT {self.POLICY_COLUMNS} FROM policies WHERE customer_id = ? ORDER BY created_at DESC",
            (customer_id,)
        )
        rows = cursor.fetchall()

        return [Policy.from_db_row(tuple(row)) for row in rows]

    def update_policy(self, policy: Policy) -> bool:
        """계약 정보 수정

        Args:
            policy: 수정할 계약 정보 (id 필수)

        Returns:
            성공 여부
        """
        if policy.id is None:
            return False

        timestamp = Policy.get_current_timestamp()

        cursor = self.connection.cursor()
        cursor.execute(
            """
            UPDATE policies
            SET customer_id = ?, insurer = ?, product_name = ?, premium = ?,
                payment_method = ?, billing_cycle = ?, billing_day = ?,
                card_issuer = ?, card_number = ?, card_expiry = ?,
                contract_start_date = ?, contract_end_date = ?,
                status = ?, next_payment_date = ?, last_payment_date = ?,
                memo = ?, updated_at = ?
            WHERE id = ?
            """,
            (
                policy.customer_id,
                policy.insurer,
                policy.product_name,
                policy.premium,
                policy.payment_method,
                policy.billing_cycle,
                policy.billing_day,
                policy.card_issuer,
                policy.card_number,
                policy.card_expiry,
                policy.contract_start_date,
                policy.contract_end_date,
                policy.status,
                policy.next_payment_date,
                policy.last_payment_date,
                policy.memo,
                timestamp,
                policy.id,
            ),
        )
        self.connection.commit()
        return cursor.rowcount > 0

    def delete_policy(self, policy_id: int) -> bool:
        """계약 삭제

        Args:
            policy_id: 삭제할 계약 ID

        Returns:
            성공 여부
        """
        cursor = self.connection.cursor()
        cursor.execute("DELETE FROM policies WHERE id = ?", (policy_id,))
        self.connection.commit()
        return cursor.rowcount > 0

    def get_upcoming_payments(self, days_ahead: int = 7) -> List[Dict]:
        """납부 임박 계약 조회 (D-7)

        Args:
            days_ahead: 며칠 이내 납부 예정 (기본: 7일)

        Returns:
            [{policy: Policy, customer: Customer, days_left: int}, ...]
        """
        today = datetime.now().date()
        end_date = today + timedelta(days=days_ahead)

        # 테이블 별칭 붙인 컬럼 목록
        p_cols = ", ".join(f"p.{c.strip()}" for c in self.POLICY_COLUMNS.split(","))
        c_cols = ", ".join(f"c.{c.strip()}" for c in self.CUSTOMER_COLUMNS.split(","))

        cursor = self.connection.cursor()
        cursor.execute(
            f"""
            SELECT {p_cols}, {c_cols}
            FROM policies p
            JOIN customers c ON p.customer_id = c.id
            WHERE p.next_payment_date BETWEEN ? AND ?
              AND p.status = 'active'
              AND p.payment_method = 'card'
            ORDER BY p.next_payment_date ASC
            """,
            (today.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))
        )
        rows = cursor.fetchall()

        results = []
        for row in rows:
            policy = Policy.from_db_row(tuple(row[:19]))
            customer = Customer.from_db_row(tuple(row[19:]))

            # 남은 일수 계산
            payment_date = datetime.strptime(policy.next_payment_date, "%Y-%m-%d").date()
            days_left = (payment_date - today).days

            results.append({
                'policy': policy,
                'customer': customer,
                'days_left': days_left
            })

        return results

    def get_overdue_policies(self) -> List[Dict]:
        """연체된 계약 조회

        Returns:
            [{policy: Policy, customer: Customer, overdue_days: int}, ...]
        """
        today = datetime.now().date()

        # 테이블 별칭 붙인 컬럼 목록
        p_cols = ", ".join(f"p.{c.strip()}" for c in self.POLICY_COLUMNS.split(","))
        c_cols = ", ".join(f"c.{c.strip()}" for c in self.CUSTOMER_COLUMNS.split(","))

        cursor = self.connection.cursor()
        cursor.execute(
            f"""
            SELECT {p_cols}, {c_cols}
            FROM policies p
            JOIN customers c ON p.customer_id = c.id
            WHERE p.status = 'overdue'
              AND p.payment_method = 'card'
            ORDER BY p.next_payment_date ASC
            """
        )
        rows = cursor.fetchall()

        results = []
        for row in rows:
            policy = Policy.from_db_row(tuple(row[:19]))
            customer = Customer.from_db_row(tuple(row[19:]))

            # 연체 일수 계산
            payment_date = datetime.strptime(policy.next_payment_date, "%Y-%m-%d").date()
            overdue_days = (today - payment_date).days

            results.append({
                'policy': policy,
                'customer': customer,
                'overdue_days': overdue_days
            })

        return results

    def mark_payment_completed(self, policy_id: int, payment_date: str) -> bool:
        """납부 완료 처리 및 다음 납부일 자동 계산

        Args:
            policy_id: 계약 ID
            payment_date: 납부 완료 날짜 (YYYY-MM-DD)

        Returns:
            성공 여부
        """
        policy = self.get_policy(policy_id)
        if not policy:
            return False

        # 다음 납부일 계산
        next_date = self.calculate_next_payment_date(
            payment_date,
            policy.billing_cycle,
            policy.billing_day
        )

        cursor = self.connection.cursor()
        cursor.execute(
            """
            UPDATE policies
            SET last_payment_date = ?,
                next_payment_date = ?,
                status = 'active',
                updated_at = ?
            WHERE id = ?
            """,
            (payment_date, next_date, Policy.get_current_timestamp(), policy_id)
        )
        self.connection.commit()
        return cursor.rowcount > 0

    def calculate_next_payment_date(
        self, current_date: str, billing_cycle: str, billing_day: int
    ) -> str:
        """다음 납부일 계산 (월말 처리 포함)

        Args:
            current_date: 기준 날짜 (YYYY-MM-DD)
            billing_cycle: 납부 주기 ("monthly" / "yearly")
            billing_day: 납부일 (1~31)

        Returns:
            다음 납부일 (YYYY-MM-DD)

        Example:
            >>> calculate_next_payment_date("2026-01-15", "monthly", 25)
            "2026-02-25"
            >>> calculate_next_payment_date("2026-01-31", "monthly", 31)
            "2026-02-28"  # 2월은 28일까지
        """
        base_date = datetime.strptime(current_date, "%Y-%m-%d").date()

        if billing_cycle == "monthly":
            # 다음 달로 이동
            next_date = base_date + relativedelta(months=1)
        elif billing_cycle == "yearly":
            # 다음 해로 이동
            next_date = base_date + relativedelta(years=1)
        else:
            # 기본값: 월납
            next_date = base_date + relativedelta(months=1)

        # 납부일 적용 (월말 자동 조정)
        try:
            next_date = next_date.replace(day=billing_day)
        except ValueError:
            # billing_day가 해당 월의 마지막 날보다 크면 (예: 2월 31일)
            # 해당 월의 마지막 날로 설정
            from calendar import monthrange
            last_day = monthrange(next_date.year, next_date.month)[1]
            next_date = next_date.replace(day=last_day)

        return next_date.strftime("%Y-%m-%d")

    def _migrate_card_field(self, cursor) -> None:
        """card_last4 → card_number 마이그레이션"""
        try:
            cursor.execute("PRAGMA table_info(policies)")
            columns = {row[1] for row in cursor.fetchall()}

            if "card_last4" in columns and "card_number" not in columns:
                # 1. 새 컬럼 추가
                cursor.execute("ALTER TABLE policies ADD COLUMN card_number TEXT")

                # 2. 기존 데이터는 복사하지 않음 (4자리 → 16자리는 불가능)
                # 사용자가 수동으로 다시 입력해야 함

                # 3. 구 컬럼 삭제를 위해 새 테이블 생성 후 데이터 복사
                cursor.execute("""
                    CREATE TABLE policies_new AS
                    SELECT
                        id, customer_id, insurer, product_name, premium,
                        payment_method, billing_cycle, billing_day,
                        card_issuer, card_number, card_expiry,
                        contract_start_date, contract_end_date,
                        status, next_payment_date, last_payment_date,
                        memo, created_at, updated_at
                    FROM policies
                """)

                cursor.execute("DROP TABLE policies")
                cursor.execute("ALTER TABLE policies_new RENAME TO policies")

                # 인덱스 재생성
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_policy_customer ON policies(customer_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_policy_next_payment ON policies(next_payment_date)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_policy_status ON policies(status)")

                self.connection.commit()
                print("[OK] Card field migration completed (card_last4 -> card_number)")
        except Exception as e:
            print(f"[WARNING] Card field migration failed (ignorable): {e}")

    def auto_update_payment_status(self) -> dict:
        """앱 시작 시 모든 계약의 납부 상태 자동 갱신

        Returns:
            {"updated": 갱신된 계약 수, "overdue": 연체 계약 수}
        """
        from datetime import datetime

        today = datetime.now().strftime("%Y-%m-%d")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 연체 상태로 변경 (카드결제만 - 계좌이체는 자동이므로 관리 불필요)
        cursor = self.connection.execute(
            """
            UPDATE policies
            SET status = 'overdue', updated_at = ?
            WHERE next_payment_date < ? AND status = 'active'
              AND payment_method = 'card'
            """,
            (timestamp, today)
        )

        overdue_count = cursor.rowcount
        self.connection.commit()

        return {
            "updated": overdue_count,
            "overdue": overdue_count
        }

    def close(self) -> None:
        """데이터베이스 연결 종료 (AP-007 대응)"""
        if self.connection:
            self.connection.close()
            self.connection = None

    def __del__(self):
        """소멸자 - 연결 자동 종료"""
        self.close()
