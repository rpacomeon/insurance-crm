# Insurance CRM

보험설계사를 위한 경량 CRM 데스크톱 앱입니다.
목표는 **많은 기능**보다 **정확한 동작**, **쉬운 사용**, **가벼운 실행**입니다.

## 현재 상태
- Phase 6-2 완료
- 다음 단계: Phase 7 (exe 빌드/배포 안정화)
- 로컬 실행 기준 테스트 통과: `tests/test_policy.py` 25개

## 빠른 시작
```bash
git clone https://github.com/rpacomeon/insurance-crm.git
cd insurance-crm
scripts\setup_env.bat
scripts\run_app.bat
```

NCP 설정은 `.env.example`을 복사해 `.env`로 만든 뒤 값만 채우면 됩니다. (`.env`는 Git에 올라가지 않음)

## 핵심 기능
- 고객 관리: 추가/수정/삭제/검색
- 보험 계약 관리: Policy CRUD, 납부일 자동 계산
- 데이터 관리: SQLite 기반 로컬 저장, 백업/복원
- CSV 내보내기

## 사용 원칙
- 신규 기능 추가보다 안정화 우선
- 문서와 실제 동작을 항상 일치
- UI는 단순하게 유지
- 배포 전 테스트 통과를 우선

## 개발 명령
```bash
pytest -q
scripts\build_exe.bat
```

## SMS 실전송
- `.env`에 NCP 값 입력
- `SMS_SEND_ENABLED=true`로 변경
- 앱 재시작 후 `Send SMS` 버튼 사용

## 문서
- `dashboard.md`: 현재 상태 단일 기준
- `docs/task.md`: 실행 태스크
- `docs/user_guide.md`: 사용자 사용법
- `docs/design_doc.md`: 설계 기준
- `docs/decision_log.md`: 의사결정 로그


## Version
- V4.0 (신용카드 필터 강화 + 납부 우선순위 운영 + 대량 더미데이터 시드)
