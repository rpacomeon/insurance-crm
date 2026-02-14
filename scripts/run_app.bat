@echo off
REM 애플리케이션 실행 스크립트

echo ====================================
echo Insurance CRM 실행
echo ====================================
echo.

REM 가상환경 확인
if not exist venv (
    echo [ERROR] 가상환경이 없습니다
    echo [INFO] setup_env.bat를 먼저 실행하세요
    pause
    exit /b 1
)

REM 가상환경 활성화
call venv\Scripts\activate.bat

REM 애플리케이션 실행
echo [INFO] 애플리케이션 시작...
echo.
python src\main.py

if errorlevel 1 (
    echo.
    echo [ERROR] 실행 중 오류 발생
    pause
    exit /b 1
)
