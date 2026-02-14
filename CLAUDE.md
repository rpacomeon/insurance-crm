# CLAUDE.md - insurance-crm 프로젝트 규칙

> **프로젝트 시작일**: 2026-02-14
> **목표**: 보험설계사용 고객 관리 시스템 (CRM) MVP 개발

---

## 📋 프로젝트 개요

### 목적
- 고객 정보를 효율적으로 관리하기 위한 데스크톱 애플리케이션
- 수기/엑셀 관리의 비효율 해결
- 전문적인 CRM 도구 제공

### 주요 기능
1. 고객 정보 관리 (CRUD)
2. 빠른 검색 기능 (이름, 전화번호)
3. 데이터 백업/복원

### 기술 스택
- **언어**: Python 3.8+
- **GUI**: tkinter (표준 라이브러리)
- **DB**: SQLite3 (로컬 파일 기반)
- **빌드**: PyInstaller (단일 exe 파일)

---

## 🎯 프로젝트 규칙 (전역 규칙 외 추가)

### Zero-Escape Policy
```
❌ 금지: 프로젝트 루트 밖에서 명령 실행
✅ 필수: 모든 작업은 이 폴더 내에서만
✅ 필수: 상대 경로 사용 (./src/main.py)
```

### 앵커 파일 시스템
```
dashboard.md      → 프로젝트 상태 (Single Source of Truth)
docs/task.md      → 태스크 체크리스트
docs/design_doc.md → 기술 명세서
```

### One-Click Setup
```
scripts/setup_env.bat  → 환경 구성 (더블클릭)
scripts/run_app.bat    → 앱 실행 (더블클릭)
```

---

## 📁 프로젝트 구조

```
insurance-crm/
├── CLAUDE.md              ← 이 파일
├── dashboard.md           ← 상태 대시보드
├── README.md              ← 프로젝트 개요
│
├── docs/
│   ├── design_doc.md      ← 기술 명세서
│   ├── task.md            ← Phase별 태스크
│   ├── user_guide.md      ← 사용자 가이드
│   ├── decision_log.md    ← 의사결정 기록
│   └── anti_patterns.md   ← 프로젝트별 실패 패턴
│
├── src/                   ← 소스 코드
│   ├── main.py
│   ├── models.py
│   ├── database.py
│   ├── gui/
│   │   ├── main_window.py
│   │   └── customer_form.py
│   └── utils/
│       ├── validators.py
│       └── file_helpers.py
│
├── tests/                 ← 테스트 코드
│   ├── test_database.py
│   ├── test_models.py
│   └── test_validators.py
│
├── scripts/               ← 실행 스크립트
│   ├── setup_env.bat
│   ├── run_app.bat
│   └── build_exe.bat
│
├── config/                ← 설정 파일
│   └── settings.json
│
└── data/                  ← 데이터베이스 파일
    └── crm.db
```

---

## 🔄 워크플로우

### AI 에이전트 작업 순서
```
1. dashboard.md 읽기 (현재 상태 파악)
2. docs/task.md 읽기 (할 일 확인)
3. Plan 수립 → 사용자 승인
4. 구현
5. 테스트 (에이전트가 먼저)
6. docs/task.md 업데이트 ✅
7. dashboard.md 업데이트
```

### Self-Check (코드 작성 전)
```
□ Anti-Patterns에 유사 패턴 있는가?
□ design_doc.md의 Data Contract와 일치하는가?
□ 테스트 코드가 있는가?
```

---

## ⚠️ 프로젝트별 Anti-Patterns

> 이 프로젝트에서 발생한 실패 패턴 기록

| 패턴 | 증상 | 해결책 |
|------|------|--------|
| AP-004 | 한글 인코딩 불일치 | SQLite UTF-8 설정 필수 |
| AP-007 | DB 파일 잠금 충돌 | 연결 1개만 유지, 종료 시 close() |
| AP-008 | PyInstaller DLL 누락 | --hidden-import 명시 |

---

## 📝 의사결정 로그

> 주요 결정사항 간략 기록 (상세: docs/decision_log.md)

| 날짜 | 결정 | 이유 |
|------|------|------|
| 2026-02-14 | tkinter + SQLite 선택 | 의존성 최소화, 로컬 우선 |
| 2026-02-14 | PyInstaller 단일 exe | 설치 불필요, 배포 간편 |

---

## 🛠️ 명령어

| 명령어 | 설명 |
|--------|------|
| `/status` | dashboard.md 기반 상태 표시 |
| `/milestone` | 마일스톤 스냅샷 저장 |
| `/report` | 비개발자용 보고서 생성 |

---

*이 파일은 ~/.claude/templates/project-CLAUDE.md에서 복사되었습니다.*
