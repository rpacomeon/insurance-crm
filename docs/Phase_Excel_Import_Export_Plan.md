# Excel Import/Export Phase Plan

## Goal
- 고객/계약 데이터를 엑셀(`.xlsx`)로 안전하게 내보내고, 다시 쉽게 밀어넣을 수 있게 한다.
- 기존 CSV 다운로드 기능은 유지하고, 엑셀 기능을 단계적으로 추가한다.

## Scope
- 대상 데이터: `customers`, `policies`
- UI 진입점: 메인 화면 하단 다운로드/복원 영역
- 파일 포맷: `.xlsx` (기본), CSV는 하위 호환

## Phase 1: Data Contract + Template (설계만)
- 엑셀 시트 구조 확정
- 컬럼 매핑 표 확정 (DB 필드 <-> 엑셀 컬럼)
- 필수/선택 컬럼 규칙 정의
- 샘플 템플릿 파일 1종 제공 (`customers`, `policies` 시트)
- 완료 기준
1. 컬럼명/타입/예시/검증 규칙이 문서화됨
2. 운영자가 그대로 입력 가능한 템플릿이 제공됨

## Phase 2: Excel Export (읽기 쉬운 출력)
- 기능
1. 전체 고객 + 계약 정보를 `.xlsx`로 내보내기
2. 시트 분리(`customers`, `policies`)
3. 헤더 고정, 열 너비 자동 조정, UTF-8/한글 깨짐 방지
- 기술
1. `openpyxl` 사용
2. 기존 `export_to_csv`와 공통 매핑 함수 분리
- 완료 기준
1. 기존 CSV와 동일 데이터가 엑셀로도 출력됨
2. 운영자가 엑셀에서 바로 필터/정렬 가능

## Phase 3: Excel Import Preview (검증 전용)
- 기능
1. 파일 선택 후 DB 반영 없이 미리보기
2. 에러 리포트 표시 (행 번호 + 사유)
3. 중복/형식 오류/필수값 누락 검증
- 핵심 검증
1. 전화번호/주민번호 형식
2. 입금방식 값 허용치 (`계좌이체`, `신용카드`, `자동이체`)
3. 계약 결제수단 값 허용치 (`card`, `transfer`)
4. 고객 참조 무결성(계약의 customer_id)
- 완료 기준
1. 운영자가 반영 전 오류를 100% 확인 가능
2. 치명 오류가 있으면 실제 반영 차단

## Phase 4: Excel Import Commit (실반영)
- 기능
1. 미리보기 통과 시 일괄 반영
2. 트랜잭션 처리(전체 성공/전체 롤백)
3. 신규/수정 모드 분리
- 안전장치
1. 반영 전 자동 백업
2. 반영 결과 요약(신규/수정/스킵/실패 건수)
- 완료 기준
1. 반영 중 오류 발생 시 DB 일관성 유지
2. 운영자가 결과를 메시지로 즉시 확인 가능

## Phase 5: 운영 고도화
- 기능
1. 템플릿 버전 관리 (`template_version`)
2. 대용량 성능 개선(배치 insert/update)
3. 감사 로그(누가 언제 어떤 파일 반영했는지)
- 완료 기준
1. 월 단위 대량 갱신에서도 안정 동작
2. 추적 가능한 운영 로그 확보

## Implementation Notes
- 의존성 추가(예정): `openpyxl`
- 권장 모듈 분리
1. `src/utils/excel_helpers.py` (입출력)
2. `src/utils/import_validators.py` (행 검증)
3. `src/gui/import_preview_dialog.py` (미리보기 UI)

## Risk and Mitigation
- 리스크: 엑셀 자유 입력으로 데이터 품질 저하
- 대응: Phase 3에서 미리보기 검증을 필수 게이트로 설정
- 리스크: 고객/계약 불일치
- 대응: 외래키/참조 검증 후에만 커밋
- 리스크: 대량 반영 중 실패
- 대응: 트랜잭션 + 자동 백업 + 롤백

## Suggested Delivery Order
1. Phase 1
2. Phase 2
3. Phase 3
4. Phase 4
5. Phase 5
