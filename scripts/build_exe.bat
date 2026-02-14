@echo off
chcp 65001 >nul 2>&1

echo ====================================
echo InsuranceCRM - exe Build
echo ====================================
echo.

REM Move to project root
cd /d "%~dp0.."

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found
    pause
    exit /b 1
)

REM Install PyInstaller if needed
python -m pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo [INFO] Installing PyInstaller...
    python -m pip install pyinstaller
)

REM Clean previous build
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build
if exist *.spec del /q *.spec

echo.
echo [INFO] Building exe...
echo.

REM Create data directory
if not exist data mkdir data

REM PyInstaller build
python -m PyInstaller ^
    --onefile ^
    --windowed ^
    --paths=src ^
    --hidden-import=tkinter ^
    --hidden-import=sqlite3 ^
    --hidden-import=database ^
    --hidden-import=models ^
    --hidden-import=gui ^
    --hidden-import=gui.main_window ^
    --hidden-import=gui.customer_form ^
    --hidden-import=gui.theme ^
    --hidden-import=utils ^
    --hidden-import=utils.validators ^
    --hidden-import=utils.file_helpers ^
    --add-data "src/gui;gui" ^
    --add-data "src/utils;utils" ^
    --add-data "src/database.py;." ^
    --add-data "src/models.py;." ^
    --name=InsuranceCRM ^
    src/main.py

if errorlevel 1 (
    echo.
    echo [ERROR] Build failed
    pause
    exit /b 1
)

REM Create data folder next to exe
if not exist dist\data mkdir dist\data

echo.
echo ====================================
echo Build complete!
echo ====================================
echo.
echo Output: dist\InsuranceCRM.exe
echo.
echo NOTE: Copy dist\InsuranceCRM.exe and
echo       dist\data\ folder together.
echo.
pause
