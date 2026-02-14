# Task List: insurance-crm

> **Total Progress**: Phase 6-2 완료 / Phase 7 대기
> **Tests**: 64 passed (2026-02-14)
> **Last Updated**: 2026-02-14

---

## Phase 1: 기반 구축 (DB 계층) ✅ 완료

- [x] 프로젝트 폴더 + CLAUDE.md + Git 초기화
- [x] `src/models.py`: Customer 데이터클래스 (to_dict, from_db_row)
- [x] `src/database.py`: DatabaseManager (CRUD + UTF-8)
- [x] `src/utils/validators.py`: 전화번호/이메일/생년월일 검증
- [x] `tests/`: 단위 테스트 24개 통과

---

## Phase 2: GUI 기본 틀 ✅ 완료

- [x] `src/gui/main_window.py`: Treeview 테이블 + 검색
- [x] 실시간 검색 (이름, 전화번호)
- [x] `scripts/setup_env.bat`, `run_app.bat`

---

## Phase 3: 고객 추가/편집 ✅ 완료

- [x] `src/gui/customer_form.py`: 모달 폼 (7필드 → 22필드로 확장됨)
- [x] 입력 검증 연결, 저장/취소

---

## Phase 4: 삭제 및 백업/복원 ✅ 완료

- [x] 삭제 확인 다이얼로그
- [x] `src/utils/file_helpers.py`: backup_database(), restore_database()

---

## Phase 5: UI/UX 확장 ✅ 완료

- [x] 좌측 테이블 + 우측 상세 패널 레이아웃
- [x] `src/gui/theme.py`: 색상/폰트/레이아웃 상수
- [x] `src/utils/export_helpers.py`: CSV 내보내기
- [x] 생일 인디케이터 (🕯️) + 유병자 인디케이터 (✚)
- [x] 필터 버튼 (전체/생일/유병/납부임박/연체)

---

## Phase 6-1: 보험 계약 관리 MVP ✅ 완료

- [x] `src/models.py`: Policy 데이터클래스 (19필드)
- [x] `src/database.py`: Policy CRUD (add/get/update/delete)
- [x] 다음 납부일 자동 계산 (월납/연납 + 월말 처리)
- [x] 고객 삭제 시 CASCADE 삭제
- [x] `src/gui/policy_form.py`: 계약 추가/편집 폼
- [x] `tests/test_policy.py`: 63개 테스트 통과

---

## Phase 6-2: 카드 16자리 + 자동 납부 체크 ✅ 완료

- [x] `card_last4` → `card_number` (16자리 평문 저장)
- [x] DB 마이그레이션 (`_migrate_card_field`)
- [x] `auto_update_payment_status()`: 앱 시작 시 연체 자동 갱신
- [x] 납부/연체 인디케이터 (💰/⚠️): **카드결제만** 대상
- [x] `SELECT *` → 명시적 컬럼 SELECT (CRM-001 해결)
- [x] 인디케이터 set 덮어쓰기 버그 수정 (CRM-002 해결)
- [x] `tests/test_policy.py`: 64개 테스트 통과

---

## Phase 7: exe 빌드 + 성능 최적화 ⚪ 대기

> **목표**: PyInstaller로 단일 exe 파일 생성, 성능 병목 1차 해결

### 7.1 PyInstaller 빌드
- [ ] `scripts/build_exe.bat` 최종 설정
- [ ] `--hidden-import` 목록 확정 (tkinter, sqlite3, dateutil)
- [ ] exe 빌드 실행 및 테스트
- [ ] Python 미설치 환경에서 실행 확인
- [ ] DLL 누락 확인 (AP-008)

### 7.2 성능 최적화 (1차)
- [ ] 검색 디바운스 추가 (300ms `after()` 패턴)
  - 파일: `src/gui/main_window.py:894` `_on_search()` 수정
  - 현재: 키입력마다 즉시 쿼리 → 수정: 300ms 대기 후 1회 실행
- [ ] 시작 시 쿼리 최적화 (`_check_payments_on_startup`)
  - 3개 쿼리 → 가능하면 1~2개로 합치기

### 7.3 문서화
- [ ] README.md 사용자 매뉴얼
- [ ] docs/user_guide.md

### 완료 조건
- [ ] exe 정상 실행 (Windows 10/11)
- [ ] 검색 시 체감 성능 개선
- [ ] 문서 완성

---

## Phase 8: UI 성능 심화 ⚪ 백로그

> **목표**: 대용량 고객(1000명+) 대응, UI 반응성 개선

### 8.1 상세 패널 위젯 재사용
- [ ] `_show_customer_detail()` 위젯 파괴/재생성 → `.config(text=)` 방식으로 전환
  - 파일: `src/gui/main_window.py:544-603`
  - 현재: 클릭마다 40+개 위젯 destroy + recreate
  - 수정: 최초 1회 생성 → 이후 텍스트만 변경

### 8.2 Python-side 필터링 → SQL WHERE
- [ ] 생일/유병 필터를 SQL 쿼리로 이전
  - 파일: `src/database.py`에 `get_birthday_customers()`, `get_medical_customers()` 추가
  - 현재: 전체 고객 로드 후 Python에서 for-loop 필터링

### 8.3 폼 성능
- [ ] MouseWheel 바인딩 누수 방지 (폼 닫을 때 unbind)
- [ ] Policy 섹션 lazy-load (필요시만 로드)

### 8.4 인덱스 추가
- [ ] `CREATE INDEX idx_customer_med ON customers(med_medication)`
- [ ] `CREATE INDEX idx_customer_resident ON customers(resident_id)`

---

## Phase 9: 클라우드 백업 (Supabase) ⚪ 백로그

- [ ] Supabase 연동 설계
- [ ] 단방향 백업 (로컬 → 클라우드)
- [ ] 복원 기능 (클라우드 → 로컬)
- [ ] 인증 (API Key → .env 파일)

---

## Phase 10: 고급 기능 ⚪ 백로그

- [ ] 가족 구성원 관리 (Family 테이블)
- [ ] 리마인더 기능 (생일, 계약 갱신일)
- [ ] 통계 대시보드 (월별 신규, 연체율 등)
- [ ] 카드 번호 AES-256 암호화 (보안 강화)

---

## 완료 기록

| 날짜 | 완료 항목 | Phase |
|------|-----------|-------|
| 2026-02-14 | 프로젝트 구조 초기화 | 1 |
| 2026-02-14 | Phase 1: DB 계층, 테스트 24개 | 1 |
| 2026-02-14 | Phase 2: GUI 메인 윈도우, 검색 | 2 |
| 2026-02-14 | Phase 3: 고객 추가/편집 폼 | 3 |
| 2026-02-14 | Phase 4: 삭제, 백업/복원 | 4 |
| 2026-02-14 | Phase 5: 테마, CSV, 레이아웃 확장 | 5 |
| 2026-02-14 | Phase 6-1: Policy CRUD + 날짜 자동계산 | 6-1 |
| 2026-02-14 | Phase 6-2: 카드 16자리 + 자동 납부 + 인디케이터 | 6-2 |

---

*태스크 완료 시 checkbox를 체크하고 dashboard.md도 업데이트하세요.*
