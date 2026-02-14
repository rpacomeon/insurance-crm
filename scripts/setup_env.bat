@echo off
REM 가상환경 설정 및 의존성 설치

echo ====================================
echo Insurance CRM - 환경 구성
echo ====================================
echo.

REM 가상환경 존재 확인
if exist venv (
    echo [INFO] 기존 가상환경 발견
) else (
    echo [INFO] 가상환경 생성 중...
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] 가상환경 생성 실패
        pause
        exit /b 1
    )
    echo [OK] 가상환경 생성 완료
)

echo.
echo [INFO] 가상환경 활성화...
call venv\Scripts\activate.bat

echo.
echo [INFO] pip 업그레이드...
python -m pip install --upgrade pip

echo.
echo [INFO] 의존성 패키지 설치...
pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo [ERROR] 패키지 설치 실패
    pause
    exit /b 1
)

echo.
echo ====================================
echo 환경 구성 완료!
echo ====================================
echo.
echo 다음 단계:
echo   1. run_app.bat 실행 (앱 실행)
echo   2. pytest (테스트 실행)
echo.
pause
