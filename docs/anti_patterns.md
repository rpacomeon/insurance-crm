# Anti-Patterns: Insurance CRM 프로젝트

> 이 프로젝트에서 발생한 실패 패턴 기록

---

## 프로젝트별 Anti-Patterns

| ID | 패턴 | 증상 | 해결책 | 발생일 |
|---|------|------|--------|--------|
| - | (아직 없음) | - | - | - |

---

## 전역 Anti-Patterns 적용

이 프로젝트에 적용되는 전역 Anti-Patterns:

### AP-004: 한글 인코딩 불일치
- **적용 위치**: database.py
- **조치**: SQLite 연결 시 UTF-8 인코딩 명시

### AP-007: 파일 잠금 충돌
- **적용 위치**: database.py, main.py
- **조치**: DB 연결 1개만 유지, 종료 시 close()

### AP-008: PyInstaller DLL 누락
- **적용 위치**: build_exe.bat
- **조치**: --hidden-import=tkinter, sqlite3 명시

### AP-012: 비밀정보 하드코딩
- **적용 위치**: 전체
- **조치**: 현재 로컬 DB만 사용, 향후 클라우드 연동 시 .env 파일 사용

---

## 패턴 기록 가이드

새로운 실패 발생 시:
1. 위 테이블에 추가
2. ID 부여 (예: CRM-001)
3. 증상, 해결책, 발생일 기록
4. CLAUDE.md에도 간략히 기록

---

*Anti-Patterns는 실패에서 배우는 시스템입니다.*
