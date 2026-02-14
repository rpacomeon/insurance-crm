# Design Document: Insurance CRM

> **Version**: 2.0.0 (Phase 6-2 반영)
> **Last Updated**: 2026-02-14

---

## 1. 시스템 개요

### 1.1 목적
보험설계사가 고객 정보 + 보험 계약을 효율적으로 관리하기 위한 데스크톱 애플리케이션

### 1.2 핵심 가치
- 빠른 고객/계약 검색
- 카드결제 계약의 자동 납부 관리 (연체 감지, 납부 임박 알림)
- 유병자/생일/운전 정보 시각적 인디케이터
- 로컬 SQLite로 안정적 데이터 저장
- 단일 exe 파일 배포

---

## 2. 아키텍처

### 2.1 계층 구조
```
┌─────────────────────────────────────┐
│   GUI Layer (tkinter)               │  ← main_window, customer_form, policy_form, theme
├─────────────────────────────────────┤
│   Business Logic                    │  ← validators, export_helpers, file_helpers
├─────────────────────────────────────┤
│   Data Layer (SQLite + models.py)   │  ← DatabaseManager, Customer, Policy
└─────────────────────────────────────┘
```

### 2.2 모듈 구조
```
src/
├── main.py              ← 엔트리포인트 (개발/PyInstaller 겸용)
├── models.py            ← Customer(22필드) + Policy(19필드)
├── database.py          ← DatabaseManager (명시적 컬럼 SELECT)
├── gui/
│   ├── main_window.py   ← 메인: 좌측 테이블 + 우측 상세 + 필터 + 인디케이터
│   ├── customer_form.py ← 고객 추가/편집 모달 (확장 필드: 의료/운전/직업)
│   ├── policy_form.py   ← 계약 추가/편집 모달 (카드 16자리)
│   └── theme.py         ← COLORS, FONTS, SPACING, SIZES, APP_INFO 상수
└── utils/
    ├── validators.py    ← validate_phone, validate_name, validate_card_number 등
    ├── file_helpers.py  ← backup_database, restore_database
    └── export_helpers.py ← export_to_csv
```

---

## 3. 데이터 모델

### 3.1 Customer 엔티티 (22 필드)
```python
@dataclass
class Customer:
    # 기본
    name: str                    # 고객명 (필수)
    phone: str                   # 전화번호 (필수, UNIQUE)
    resident_id: str             # 주민등록번호 (YYMMDD-NNNNNNN)
    birth_date: Optional[str]    # 생년월일
    address: Optional[str]       # 주소
    email: Optional[str]         # 이메일
    memo: Optional[str]          # 메모

    # 보험 관련
    driving_type: str            # "none" / "personal" / "commercial"
    commercial_detail: Optional[str]  # "taxi", "construction" (콤마 구분)
    payment_method: Optional[str]     # "계좌이체" / "신용카드" / "자동이체"
    occupation: Optional[str]         # 직업

    # 건강 정보
    med_medication: Optional[str]      # 약 복용 (콤마 구분: "고혈압약,당뇨약")
    med_hospitalized: bool             # 입원/수술 이력
    med_hospital_detail: Optional[str] # 입원/수술 상세
    med_recent_exam: bool              # 최근 3개월 진찰
    med_recent_exam_detail: Optional[str]
    med_5yr_diagnosis: Optional[str]   # 5년 이내 진단 (콤마 구분)
    med_5yr_custom: Optional[str]      # 사용자 정의 진단

    # 고지
    notification_content: Optional[str]

    # 시스템
    id: Optional[int]
    created_at: Optional[str]
    updated_at: Optional[str]
```

### 3.2 Policy 엔티티 (19 필드)
```python
@dataclass
class Policy:
    customer_id: int
    insurer: str            # 보험사
    product_name: str       # 상품명
    premium: int            # 보험료

    payment_method: str     # "card" / "transfer"
    billing_cycle: str      # "monthly" / "yearly"
    billing_day: int        # 1~31

    card_issuer: Optional[str]   # 카드사
    card_number: Optional[str]   # 16자리 (예: "1234-5678-9012-3456") - 평문
    card_expiry: Optional[str]   # "MM/YY"

    contract_start_date: str
    contract_end_date: Optional[str]

    status: str             # "active" / "overdue" / "terminated"
    next_payment_date: str  # 자동 계산
    last_payment_date: Optional[str]

    memo: Optional[str]
    id: Optional[int]
    created_at: Optional[str]
    updated_at: Optional[str]
```

### 3.3 DB 스키마
```sql
-- customers: 22 컬럼
CREATE TABLE customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    phone TEXT NOT NULL UNIQUE,
    resident_id TEXT DEFAULT '',
    birth_date TEXT, address TEXT, email TEXT, memo TEXT,
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

-- policies: 19 컬럼
CREATE TABLE policies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL,
    insurer TEXT NOT NULL, product_name TEXT NOT NULL, premium INTEGER NOT NULL,
    payment_method TEXT NOT NULL, billing_cycle TEXT NOT NULL, billing_day INTEGER NOT NULL,
    card_issuer TEXT, card_number TEXT, card_expiry TEXT,
    contract_start_date TEXT NOT NULL, contract_end_date TEXT,
    status TEXT DEFAULT 'active',
    next_payment_date TEXT NOT NULL, last_payment_date TEXT,
    memo TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE
);

-- 인덱스
CREATE INDEX idx_customer_name ON customers(name);
CREATE INDEX idx_customer_phone ON customers(phone);
CREATE INDEX idx_policy_customer ON policies(customer_id);
CREATE INDEX idx_policy_next_payment ON policies(next_payment_date);
CREATE INDEX idx_policy_status ON policies(status);
```

---

## 4. DatabaseManager API

### 4.1 핵심 설계 원칙

**명시적 컬럼 SELECT** (CRM-001 해결):
```python
# ❌ 금지: SELECT * (ALTER TABLE 이후 컬럼 순서 불일치)
# ✅ 필수: 명시적 컬럼 목록 사용
CUSTOMER_COLUMNS = "id, name, phone, resident_id, birth_date, ..."
POLICY_COLUMNS = "id, customer_id, insurer, product_name, ..."
```

**카드결제만 납부 관리**:
```python
# 연체 자동 갱신, 납부 임박 조회, 연체 조회 모두 card만 대상
WHERE payment_method = 'card'
```

### 4.2 Customer CRUD
```python
add_customer(customer: Customer) -> int
get_customer(customer_id: int) -> Optional[Customer]
get_all_customers() -> List[Customer]
search_customers(keyword: str) -> List[Customer]
update_customer(customer: Customer) -> bool
delete_customer(customer_id: int) -> bool
```

### 4.3 Policy CRUD
```python
add_policy(policy: Policy) -> int
get_policy(policy_id: int) -> Optional[Policy]
get_policies_by_customer(customer_id: int) -> List[Policy]
update_policy(policy: Policy) -> bool
delete_policy(policy_id: int) -> bool
```

### 4.4 납부 관리 (카드결제만)
```python
get_upcoming_payments(days_ahead: int = 7) -> List[Dict]
    # Returns: [{policy: Policy, customer: Customer, days_left: int}]
    # 조건: status='active' AND payment_method='card'

get_overdue_policies() -> List[Dict]
    # Returns: [{policy: Policy, customer: Customer, overdue_days: int}]
    # 조건: status='overdue' AND payment_method='card'

mark_payment_completed(policy_id: int, payment_date: str) -> bool
    # → status='active', next_payment_date 자동계산

auto_update_payment_status() -> dict
    # 앱 시작 시 실행: active → overdue (카드결제만)
    # Returns: {"updated": int, "overdue": int}
```

### 4.5 유틸리티
```python
calculate_next_payment_date(current_date, billing_cycle, billing_day) -> str
    # 월납: 다음 달 billing_day (월말 처리 포함)
    # 연납: 다음 해 동일 월 billing_day
```

---

## 5. GUI 레이아웃

### 5.1 메인 윈도우 (`main_window.py`)
```
┌────────────────────────────────────────────────────────┐
│  [검색: ________] [전체] [생일] [유병] [납부임박] [연체]  │
├──────────────────────────────┬─────────────────────────┤
│  🕯️ ✚ 💰 ⚠️ 이름  전화번호...   │  고객 상세 정보          │
│  🕯️    김철수 010-1111-0001     │  이름: 김철수             │
│     ✚  강동원 010-2222-0006     │  전화: 010-1111-0001     │
│        손예진 010-4444-0016     │  주민: 850214-1234567    │
│                                │  ...                     │
│                                │  [보험 계약 목록]         │
│                                │  삼성생명 종신보험 5만원  │
├──────────────────────────────┴─────────────────────────┤
│  총 30명 (전체 30명 | 생일자 5명 | 유병자 15명)          │
│  [새 고객] [수정] [삭제] [백업] [복원] [CSV] [납부완료]  │
└────────────────────────────────────────────────────────┘
```

### 5.2 인디케이터 규칙
| 아이콘 | 조건 | 데이터 소스 |
|--------|------|-------------|
| 🕯️ | 주민번호 MMDD = 오늘 | `customer.resident_id` |
| ✚ | 약 복용 OR 5년 진단 OR 최근 진찰 OR 사용자 진단 | `customer.med_*` 필드 |
| 💰 | 오늘 납부 예정 (카드결제만) | `policy.next_payment_date = today AND payment_method = 'card'` |
| ⚠️ | 연체 (카드결제만) | `policy.status = 'overdue' AND payment_method = 'card'` |

### 5.3 필터 모드
- `all`: 전체 표시
- `birthday`: 오늘 생일인 고객만
- `medical`: 유병 정보 있는 고객만
- `upcoming_payment`: 7일 이내 카드 납부 예정 고객
- `overdue`: 카드 연체 고객

---

## 6. 입력 검증

| 필드 | 규칙 | 함수 |
|------|------|------|
| 이름 | 1자 이상, 공백 불가 | `validate_name()` |
| 전화번호 | `^\d{2,3}-?\d{3,4}-?\d{4}$` | `validate_phone()` |
| 주민번호 | `NNNNNN-NNNNNNN` (13자리) | `validate_resident_id()` |
| 이메일 | 표준 이메일 정규식 | `validate_email()` |
| 생년월일 | `YYYY-MM-DD` | `validate_birth_date()` |
| 보험료 | 양의 정수 | `validate_premium()` |
| 납부일 | 1~31 | `validate_billing_day()` |
| 카드번호 | 16자리 숫자 (하이픈 허용) | `validate_card_number()` |
| 카드유효기간 | `MM/YY` | `validate_card_expiry()` |

---

## 7. Anti-Patterns 회피

| ID | 패턴 | 적용 위치 |
|----|------|-----------|
| AP-004 | 한글 인코딩 | `PRAGMA encoding = 'UTF-8'` |
| AP-007 | DB 파일 잠금 | 연결 1개만 유지, close() |
| AP-008 | PyInstaller DLL | `--hidden-import` |
| CRM-001 | SELECT * 컬럼 순서 | 명시적 컬럼 목록 사용 |
| CRM-002 | set 덮어쓰기 | 인디케이터 set 1회 계산 |

---

## 8. 보안

### 8.1 카드 번호 평문 저장
- 현재: 평문 저장 (로컬 DB, 사용자 요청)
- 위험: DB 파일 접근 시 카드 번호 노출
- 향후: Phase 10에서 AES-256 암호화 옵션 추가

### 8.2 SQL Injection 방지
- 모든 쿼리에서 `?` 파라미터 바인딩 사용

---

## 9. 성능 현황

### 9.1 현재 측정값 (30명 + 43계약)
- 앱 시작: ~0.5초
- 고객 검색: ~0.05초
- 계약 조회: ~0.03초

### 9.2 알려진 병목 (Phase 7-8에서 해결)
| 병목 | 위치 | 영향도 | 해결 Phase |
|------|------|--------|-----------|
| 검색 디바운스 없음 | main_window.py:894 | HIGH | 7 |
| 시작 시 3개 쿼리 | main_window.py:113-138 | HIGH | 7 |
| 위젯 파괴/재생성 | main_window.py:544-603 | MEDIUM | 8 |
| Python-side 필터링 | main_window.py:801-822 | MEDIUM | 8 |

---

*Design Document v2.0 - Phase 6-2 반영*
