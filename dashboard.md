# Project Dashboard: insurance-crm

> **Status**: Active
> **Phase**: 6-2 완료 -> 7 대기
> **Principle**: 정확성/단순성/경량 우선
> **Last Updated**: 2026-02-15

## Current Focus
- [x] 고객 CRUD + 검색 + 백업/복원
- [x] 보험 계약 CRUD + 납부일 자동 계산
- [x] 카드 필드 `card_number` 표준화
- [ ] PyInstaller exe 빌드 안정화
- [ ] 배포 문서 최종 점검

## Health
- 정책 테스트: `tests/test_policy.py` 통과
- 주요 리스크: 빌드/배포 환경 차이(Phase 7)

## Next (Phase 7)
1. `scripts/build_exe.bat`로 exe 빌드
2. Windows 10/11 실행 확인
3. README/가이드 배포 검수

## Source of Truth
- 상태 변경은 이 파일을 먼저 업데이트
