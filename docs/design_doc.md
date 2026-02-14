# Design Document: Insurance CRM

> **Version**: 1.0.0
> **Last Updated**: 2026-02-14
> **Author**: Claude Code

---

## 1. 시스템 개요

### 1.1 목적
보험설계사가 고객 정보를 효율적으로 관리하기 위한 데스크톱 애플리케이션

### 1.2 핵심 가치
- 빠른 고객 정보 검색
- 안정적인 로컬 데이터 저장
- 간편한 백업/복원
- 설치 불필요 (단일 exe 파일)

---

## 2. 아키텍처

### 2.1 계층 구조
```
┌─────────────────────────┐
│   GUI Layer (tkinter)   │  ← 사용자 인터페이스
├─────────────────────────┤
│   Business Logic        │  ← 검증, 변환, 비즈니스 규칙
├─────────────────────────┤
│   Data Layer (SQLite)   │  ← 데이터 저장/조회
└─────────────────────────┘
```

### 2.2 모듈 구조
- **models.py**: 데이터 모델 (Customer)
- **database.py**: DB 연결 및 CRUD
- **gui/**: 사용자 인터페이스
  - main_window.py: 메인 화면
  - customer_form.py: 고객 추가/편집 폼
- **utils/**: 유틸리티 함수
  - validators.py: 입력 검증
  - file_helpers.py: 백업/복원

---

## 3. 데이터 모델

### 3.1 Customer 엔티티
```python
@dataclass
class Customer:
    name: str              # 고객명 (필수)
    phone: str             # 전화번호 (필수, 중복 불가)
    birth_date: Optional[str]   # 생년월일 (YYYY-MM-DD)
    address: Optional[str]      # 주소
    email: Optional[str]        # 이메일
    memo: Optional[str]         # 메모
    id: Optional[int]           # 자동 증가 ID
    created_at: Optional[str]   # 생성일시
    updated_at: Optional[str]   # 수정일시
```

### 3.2 데이터베이스 스키마
```sql
CREATE TABLE customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    phone TEXT NOT NULL UNIQUE,
    birth_date TEXT,
    address TEXT,
    email TEXT,
    memo TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE INDEX idx_customer_name ON customers(name);
CREATE INDEX idx_customer_phone ON customers(phone);
```

---

## 4. API 명세 (DatabaseManager)

### 4.1 CRUD 메서드
```python
class DatabaseManager:
    def add_customer(self, customer: Customer) -> int
        """새 고객 추가, 생성된 ID 반환"""

    def get_customer(self, customer_id: int) -> Optional[Customer]
        """ID로 고객 조회"""

    def get_all_customers(self) -> List[Customer]
        """모든 고객 조회"""

    def search_customers(self, keyword: str) -> List[Customer]
        """이름 또는 전화번호로 검색"""

    def update_customer(self, customer: Customer) -> bool
        """고객 정보 수정"""

    def delete_customer(self, customer_id: int) -> bool
        """고객 삭제"""
```

---

## 5. 입력 검증 규칙

### 5.1 필수 필드
- **이름**: 공백 불가, 1자 이상
- **전화번호**: 공백 불가, 형식 검증

### 5.2 선택 필드
- **전화번호 형식**: `^\d{2,3}-?\d{3,4}-?\d{4}$`
- **이메일 형식**: 표준 이메일 정규식
- **생년월일 형식**: YYYY-MM-DD (날짜 유효성 확인)

---

## 6. 에러 처리 전략

### 6.1 표준 반환 형식
```python
Result = TypedDict('Result', {
    'success': bool,
    'data': Any,
    'error': Optional[str]
})
```

### 6.2 에러 유형
- **ValidationError**: 입력 검증 실패
- **DatabaseError**: DB 연결/쿼리 실패
- **FileError**: 백업/복원 파일 오류

---

## 7. Anti-Patterns 회피

### 7.1 AP-004: 한글 인코딩
```python
# SQLite 연결 시 UTF-8 명시
self.connection = sqlite3.connect(str(self.db_path))
self.connection.execute("PRAGMA encoding = 'UTF-8'")
```

### 7.2 AP-007: 파일 잠금
- DB 연결은 프로그램당 1개만
- 종료 시 `connection.close()` 필수

### 7.3 AP-008: PyInstaller DLL
```bash
pyinstaller --onefile --windowed \
    --hidden-import=tkinter \
    --hidden-import=sqlite3 \
    src/main.py
```

---

## 8. 성능 고려사항

### 8.1 검색 최적화
- 인덱스 활용 (name, phone 컬럼)
- LIKE 쿼리 사용 시 앞부분 매칭 우선

### 8.2 대용량 데이터
- 현재 MVP는 최대 1,000명 고객 기준
- 향후 페이지네이션 고려

---

## 9. 보안

### 9.1 데이터 보호
- 로컬 DB 파일만 사용
- 네트워크 전송 없음
- 백업 파일 암호화 (향후)

### 9.2 입력 검증
- SQL Injection 방지 (파라미터 바인딩)
- Path Traversal 방지 (백업 경로 검증)

---

## 10. 향후 확장

### 10.1 Phase 6+
- 가족 구성원 관리
- 보험 계약 관리
- 리마인더 기능
- 클라우드 동기화 (Supabase)

---

*Design Document v1.0*
