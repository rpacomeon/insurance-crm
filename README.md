# Insurance CRM - 보험설계사 고객 관리 시스템

> 보험설계사를 위한 간편한 고객 정보 관리 데스크톱 애플리케이션

## 📌 주요 기능

- ✅ **고객 정보 관리**: 이름, 전화번호, 생년월일, 주소, 이메일, 메모 관리
- 🔍 **빠른 검색**: 이름 또는 전화번호로 실시간 검색
- 💾 **데이터 백업/복원**: 간편한 백업 및 복원 기능
- 🖥️ **단일 실행 파일**: 설치 불필요, exe 파일만 실행

## 🚀 빠른 시작 (Quick Start)

### ⚡ 3단계로 바로 실행하기

```bash
# 1. 저장소 클론
git clone https://github.com/rpacomeon/insurance-crm.git
cd insurance-crm

# 2. 환경 설정 (최초 1회만)
scripts\setup_env.bat

# 3. 프로그램 실행
scripts\run_app.bat
```

> **필수 요구사항**: Python 3.8 이상이 설치되어 있어야 합니다.
> Python 설치: https://www.python.org/downloads/

---

### 📦 다른 설치 방법

#### 방법 1: exe 파일 실행 (가장 쉬움)
1. [Releases](https://github.com/rpacomeon/insurance-crm/releases)에서 `InsuranceCRM.exe` 다운로드
2. 더블클릭으로 실행
3. Python 설치 불필요!

#### 방법 2: GitHub Desktop 사용
1. [GitHub Desktop](https://desktop.github.com/) 설치
2. `File` → `Clone Repository` → URL 입력: `https://github.com/rpacomeon/insurance-crm`
3. 클론 완료 후 `scripts\setup_env.bat` 실행
4. `scripts\run_app.bat`으로 프로그램 실행

## 📖 사용 방법

### 고객 추가
1. "새 고객 추가" 버튼 클릭
2. 정보 입력 (이름, 전화번호 필수)
3. "저장" 버튼 클릭

### 고객 검색
1. 검색창에 이름 또는 전화번호 입력
2. 자동으로 결과 필터링

### 고객 수정
1. 목록에서 고객 선택
2. "수정" 버튼 클릭
3. 정보 수정 후 저장

### 고객 삭제
1. 목록에서 고객 선택
2. "삭제" 버튼 클릭
3. 확인 메시지에서 "예" 선택

### 데이터 백업
1. "백업" 버튼 클릭
2. 백업 파일 저장 위치 선택
3. 백업 파일 생성 완료

### 데이터 복원
1. "복원" 버튼 클릭
2. 백업 파일 선택
3. 데이터 복원 완료

## 💻 기술 스택

- **언어**: Python 3.8+
- **GUI**: tkinter (표준 라이브러리)
- **데이터베이스**: SQLite3 (로컬 파일)
- **빌드**: PyInstaller

## 📁 프로젝트 구조

```
insurance-crm/
├── src/                   # 소스 코드
│   ├── main.py            # 진입점
│   ├── models.py          # 데이터 모델
│   ├── database.py        # DB 로직
│   ├── gui/               # GUI 모듈
│   └── utils/             # 유틸리티
├── tests/                 # 테스트 코드
├── scripts/               # 실행 스크립트
├── data/                  # 데이터베이스 파일
└── docs/                  # 문서
```

## 🛠️ 개발자 정보

### 요구사항
- Python 3.8 이상
- pip (패키지 관리자)

### 개발 환경 설정
```bash
# 가상환경 생성 및 활성화
python -m venv venv
venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt
```

### 테스트 실행
```bash
pytest tests/
```

### exe 빌드
```bash
scripts\build_exe.bat
```

## 📝 라이선스

이 프로젝트는 개인 사용 목적으로 개발되었습니다.

## 📞 문의

문제가 발생하거나 기능 제안이 있으시면 이슈를 등록해주세요.

---

**Version**: 1.0.0 (MVP)
**Last Updated**: 2026-02-14
