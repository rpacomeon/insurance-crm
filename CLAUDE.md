# CLAUDE.md - insurance-crm 프로젝트 규칙

> **프로젝트 시작일**: 2026-02-14
> **현재 상태**: Phase 6-2 완료 (v2.0) / Phase 7 대기
> **목표**: 보험설계사용 고객+계약 관리 시스템 (CRM)
> **테스트**: 64 passed

---

## 프로젝트 개요

### 목적
- 보험설계사가 고객 정보 + 보험 계약을 효율적으로 관리하는 데스크톱 앱
- 카드결제 계약의 납부/연체 자동 관리
- 유병자/생일/운전 정보 시각적 인디케이터

### 주요 기능 (현재)
1. 고객 정보 관리 (22필드 CRUD)
2. 보험 계약 관리 (19필드 CRUD + 날짜 자동계산)
3. 검색 (이름, 전화번호)
4. 인디케이터 (생일/유병/납부/연체)
5. 필터 (전체/생일/유병/납부임박/연체)
6. 백업/복원, CSV 내보내기

### 기술 스택
- **Python 3.8+** / **tkinter** / **SQLite3** / **PyInstaller**
- **의존성**: `python-dateutil` (날짜 계산)

---

## 핵심 규칙

### 코드 규칙
```
1. SELECT * 절대 금지 → CUSTOMER_COLUMNS / POLICY_COLUMNS 상수 사용 (CRM-001)
2. 납부/연체 관리는 카드결제(card)만 대상 → WHERE payment_method = 'card'
3. 카드 번호 16자리 평문 저장 (사용자 요청)
4. 테스트: python -m pytest tests/ -v (64개 전체 통과 필수)
```

### 앵커 파일 (작업 시작 전 반드시 읽기)
```
dashboard.md        → 프로젝트 상태 (Single Source of Truth)
docs/task.md        → Phase별 태스크 체크리스트
docs/design_doc.md  → 기술 명세서 (v2.0)
```

### AI 에이전트 작업 순서
```
1. dashboard.md 읽기 → 현재 상태 파악
2. docs/task.md 읽기 → 할 일 확인
3. docs/anti_patterns.md 읽기 → 실패 패턴 확인
4. Plan 수립 → 사용자 승인
5. 구현 → 테스트 → 문서 업데이트
```

---

## 프로젝트 구조

```
insurance-crm/
├── CLAUDE.md                ← 이 파일 (프로젝트 규칙)
├── dashboard.md             ← 상태 대시보드
├── docs/
│   ├── design_doc.md        ← 기술 명세서 v2.0
│   ├── task.md              ← Phase별 태스크
│   ├── decision_log.md      ← 의사결정 기록
│   └── anti_patterns.md     ← 실패 패턴 (CRM-001~003)
├── src/
│   ├── main.py              ← 엔트리포인트
│   ├── models.py            ← Customer(22필드) + Policy(19필드)
│   ├── database.py          ← DatabaseManager (CUSTOMER_COLUMNS, POLICY_COLUMNS)
│   ├── gui/
│   │   ├── main_window.py   ← 메인 윈도우 (테이블+상세+인디케이터)
│   │   ├── customer_form.py ← 고객 폼 (의료/운전/직업/고지)
│   │   ├── policy_form.py   ← 계약 폼 (카드 16자리)
│   │   └── theme.py         ← 색상/폰트 상수
│   └── utils/
│       ├── validators.py    ← 입력 검증
│       ├── file_helpers.py  ← 백업/복원
│       └── export_helpers.py ← CSV 내보내기
├── tests/                   ← 64개 테스트
├── scripts/
│   ├── create_dummy_data.py ← 더미 30명+43계약
│   └── run_with_dummy.py    ← 더미 DB로 실행
└── data/
    ├── crm.db               ← 운영 DB
    └── crm_dummy.db         ← 더미 DB
```

---

## Anti-Patterns (코드 작성 전 확인)

| ID | 패턴 | 핵심 |
|----|------|------|
| CRM-001 | SELECT * 컬럼 순서 | ALTER TABLE 후 물리 순서 변경 → 명시적 컬럼 필수 |
| CRM-002 | set 덮어쓰기 | 인디케이터 set 1회 계산, 재할당 금지 |
| CRM-003 | 고객/계약 결제방식 불일치 | customer.payment_method ↔ policy.payment_method 일관성 |
| AP-004 | 한글 인코딩 | SQLite UTF-8 설정 필수 |
| AP-007 | DB 파일 잠금 | 연결 1개, 종료 시 close() |
| AP-008 | PyInstaller DLL | --hidden-import 명시 |

---

## 의사결정 로그 (요약)

| 결정 | 이유 |
|------|------|
| tkinter + SQLite | 의존성 최소화, 로컬 우선 |
| SELECT * 금지 | CRM-001: 컬럼 순서 불일치 버그 |
| 카드 번호 평문 | 사용자 요청: 로컬이므로 속도 우선 |
| 카드결제만 납부 관리 | 계좌이체는 자동이체이므로 관리 불필요 |

---

## 다음 Phase (Phase 7)

```
목표: PyInstaller exe 빌드 + 검색 디바운스
파일: docs/task.md의 Phase 7 섹션 참조
```

---

*v2.0 - Phase 6-2 완료 (2026-02-14)*
