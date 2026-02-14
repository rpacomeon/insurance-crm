# Task List: insurance-crm

> **Total Progress**: █████████░ 90%
> **Current Phase**: 5 - 배포 준비
> **Last Updated**: 2026-02-14

---

## Phase 1: 기반 구축 (DB 계층) - 완료

### 1.1 환경 설정
- [x] 프로젝트 폴더 생성
- [x] CLAUDE.md 설정
- [x] dashboard.md 생성
- [x] Git 저장소 초기화
- [x] .gitignore 설정
- [x] requirements.txt 작성

### 1.2 데이터 모델 구축
- [x] src/models.py 작성
  - [x] Customer 데이터클래스 정의
  - [x] to_dict() 메서드 구현
  - [x] from_db_row() 메서드 구현
- [x] tests/test_models.py 작성

### 1.3 데이터베이스 계층
- [x] src/database.py 작성
  - [x] DatabaseManager 클래스
  - [x] DB 연결 및 테이블 생성
  - [x] CRUD 메서드 구현
  - [x] UTF-8 인코딩 설정 (AP-004)
- [x] tests/test_database.py 작성
- [x] 단위 테스트 실행 및 통과

### 1.4 유틸리티 함수
- [x] src/utils/validators.py 작성
  - [x] validate_phone() 함수
  - [x] validate_email() 함수
  - [x] validate_birth_date() 함수
- [x] tests/test_validators.py 작성

**Phase 1 완료 조건**:
- [x] 모든 단위 테스트 통과
- [x] DB CRUD 동작 확인
- [x] 한글 데이터 저장/조회 정상 동작

---

## Phase 2: GUI 기본 틀 (고객 목록 및 검색) - 완료

### 2.1 메인 윈도우
- [x] src/gui/main_window.py 작성
  - [x] 검색 프레임 (Entry + 버튼)
  - [x] Treeview 테이블 구성
  - [x] 하단 버튼 배치
- [x] 고객 목록 표시 기능
- [x] 테스트 데이터로 동작 확인

### 2.2 검색 기능
- [x] 실시간 검색 구현
  - [x] 이름 검색
  - [x] 전화번호 검색
- [x] 검색 결과 테이블 업데이트

### 2.3 실행 스크립트
- [x] scripts/setup_env.bat 작성
- [x] scripts/run_app.bat 작성
- [x] 스크립트 동작 확인

**Phase 2 완료 조건**:
- [x] 메인 윈도우 실행
- [x] 고객 목록 조회
- [x] 검색 기능 동작

---

## Phase 3: 고객 추가/편집 (CRUD 완성) - 완료

### 3.1 고객 폼 모달
- [x] src/gui/customer_form.py 작성
  - [x] 입력 필드 7개 배치
  - [x] 검증 로직 연결
  - [x] 저장/취소 버튼
- [x] 폼 레이아웃 디자인

### 3.2 추가 기능
- [x] "새 고객 추가" 버튼 연결
- [x] 폼 입력 검증
- [x] DB 저장 및 목록 갱신

### 3.3 편집 기능
- [x] "수정" 버튼 연결
- [x] 선택된 고객 정보 로드
- [x] 수정 저장 및 목록 갱신

**Phase 3 완료 조건**:
- [x] 고객 추가 동작
- [x] 고객 수정 동작
- [x] 입력 검증 에러 메시지 표시

---

## Phase 4: 삭제 및 백업 (데이터 관리) - 완료

### 4.1 삭제 기능
- [x] "삭제" 버튼 연결
- [x] 확인 메시지 다이얼로그
- [x] DB 삭제 및 목록 갱신

### 4.2 백업/복원
- [x] src/utils/file_helpers.py 작성
  - [x] backup_database() 함수
  - [x] restore_database() 함수
- [x] "백업" 버튼 연결
- [x] "복원" 버튼 연결
- [x] 파일 다이얼로그 구현

### 4.3 통합 테스트
- [x] 전체 시나리오 테스트
- [x] 버그 수정

**Phase 4 완료 조건**:
- [x] 삭제 기능 동작
- [x] 백업 파일 생성
- [x] 복원 기능 동작

---

## Phase 5: 배포 준비 (exe 빌드) - 진행중

### 5.1 빌드 준비
- [x] requirements.txt 최종 정리
- [x] PyInstaller 설정 작성
- [x] scripts/build_exe.bat 작성

### 5.2 exe 빌드
- [ ] PyInstaller 빌드 실행
- [ ] DLL 누락 확인 및 수정 (AP-008)
- [ ] exe 테스트 (Python 미설치 환경)

### 5.3 문서화
- [ ] README.md 사용자 매뉴얼 작성
- [ ] docs/user_guide.md 완성
- [ ] 스크린샷 추가

### 5.4 최종 검증
- [ ] 배포 전 체크리스트 확인
- [ ] Windows 10/11 호환성 테스트
- [ ] 사용자 승인

**Phase 5 완료 조건**:
- [ ] exe 파일 정상 실행
- [ ] 모든 기능 동작
- [ ] 문서 완성

---

## Backlog (향후 확장)

MVP 이후 추가 가능한 기능:
- [ ] 가족 구성원 관리
- [ ] 보험 계약 관리
- [ ] 리마인더 기능 (생일, 계약 갱신일)
- [ ] 클라우드 동기화 (Supabase)

---

## Blocked Tasks

현재 진행 불가한 작업:

| 태스크 | 블로커 | 해결 방법 |
|--------|--------|-----------|
| - | - | - |

---

## 완료 기록

| 날짜 | 완료 항목 | Phase |
|------|-----------|-------|
| 2026-02-14 | 프로젝트 구조 초기화 | 1 |
| 2026-02-14 | 앵커 파일 생성 | 1 |
| 2026-02-14 | Phase 1 완료: DB 계층, 테스트 24개 통과 | 1 |
| 2026-02-14 | Phase 2 완료: GUI 메인 윈도우, 검색 | 2 |
| 2026-02-14 | Phase 3 완료: 고객 추가/편집 폼 | 3 |
| 2026-02-14 | Phase 4 완료: 삭제, 백업/복원 | 4 |

---

*태스크 완료 시 checkbox를 체크하고 dashboard.md의 Progress를 업데이트하세요.*
