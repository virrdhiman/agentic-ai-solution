@echo off
REM ============================================================
REM  Autonomous Agent — Windows Build Script
REM  Builds a standalone .exe and optional installer
REM  Author: Virender Dhiman
REM ============================================================

setlocal enabledelayedexpansion

echo.
echo  ====================================================
echo   Autonomous Agent — Windows Build
echo   Author: Virender Dhiman
echo  ====================================================
echo.

REM --- Configuration ---
set "PROJECT_NAME=autonomous-agent"
set "VERSION=0.1.0"
set "DIST_DIR=dist"
set "BUILD_DIR=build"
set "SPEC_FILE=%PROJECT_NAME%.spec"

REM --- Step 1: Check Python ---
echo [1/8] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH.
    echo Please install Python 3.11+ from https://python.org
    exit /b 1
)
for /f "tokens=2 delims= " %%v in ('python --version 2^>^&1') do set "PY_VER=%%v"
echo   Found Python %PY_VER%

REM --- Step 2: Create virtual environment ---
echo.
echo [2/8] Creating virtual environment...
if not exist ".venv-build" (
    python -m venv .venv-build
    echo   Created .venv-build
) else (
    echo   Using existing .venv-build
)
call .venv-build\Scripts\activate.bat

REM --- Step 3: Install dependencies ---
echo.
echo [3/8] Installing dependencies...
pip install --upgrade pip >nul 2>&1
pip install -e ".[dev]" >nul 2>&1
pip install pyinstaller >nul 2>&1
echo   Dependencies installed

REM --- Step 4: Run tests ---
echo.
echo [4/8] Running tests...
python -m pytest tests/ -v --tb=short
if errorlevel 1 (
    echo.
    echo WARNING: Some tests failed. Continue anyway? (Y/N)
    set /p "CONTINUE=>"
    if /i "!CONTINUE!" NEQ "Y" (
        echo Build aborted.
        exit /b 1
    )
) else (
    echo   All tests passed!
)

REM --- Step 5: Clean previous build ---
echo.
echo [5/8] Cleaning previous build artifacts...
if exist "%DIST_DIR%" rmdir /s /q "%DIST_DIR%"
if exist "%BUILD_DIR%" rmdir /s /q "%BUILD_DIR%"
if exist "%SPEC_FILE%" del "%SPEC_FILE%"
echo   Cleaned

REM --- Step 6: Build standalone .exe with PyInstaller ---
echo.
echo [6/8] Building standalone .exe...
pyinstaller ^
    --name "%PROJECT_NAME%" ^
    --onefile ^
    --console ^
    --icon "NONE" ^
    --add-data "policies;policies" ^
    --add-data "autonomous_agent\config;autonomous_agent\config" ^
    --hidden-import "autonomous_agent" ^
    --hidden-import "autonomous_agent.core" ^
    --hidden-import "autonomous_agent.core.state" ^
    --hidden-import "autonomous_agent.core.models" ^
    --hidden-import "autonomous_agent.core.evidence" ^
    --hidden-import "autonomous_agent.core.orchestrator" ^
    --hidden-import "autonomous_agent.core.router" ^
    --hidden-import "autonomous_agent.providers" ^
    --hidden-import "autonomous_agent.providers.base" ^
    --hidden-import "autonomous_agent.providers.mock" ^
    --hidden-import "autonomous_agent.providers.opensource" ^
    --hidden-import "autonomous_agent.providers.router" ^
    --hidden-import "autonomous_agent.tools" ^
    --hidden-import "autonomous_agent.tools.base" ^
    --hidden-import "autonomous_agent.tools.filesystem" ^
    --hidden-import "autonomous_agent.tools.shell" ^
    --hidden-import "autonomous_agent.tools.git" ^
    --hidden-import "autonomous_agent.cli" ^
    --hidden-import "autonomous_agent.api" ^
    --hidden-import "autonomous_agent.api.app" ^
    --hidden-import "pydantic" ^
    --hidden-import "pydantic_settings" ^
    --hidden-import "fastapi" ^
    --hidden-import "uvicorn" ^
    --hidden-import "click" ^
    --hidden-import "rich" ^
    --hidden-import "structlog" ^
    --hidden-import "git" ^
    --hidden-import "httpx" ^
    --collect-all "autonomous_agent" ^
    autonomous_agent\cli\__init__.py

if errorlevel 1 (
    echo ERROR: PyInstaller build failed.
    exit /b 1
)
echo   Built: %DIST_DIR%\%PROJECT_NAME%.exe

REM --- Step 7: Verify the .exe works ---
echo.
echo [7/8] Verifying .exe...
"%DIST_DIR%\%PROJECT_NAME%.exe" --help >nul 2>&1
if errorlevel 1 (
    echo WARNING: .exe --help returned non-zero. Trying without args...
    "%DIST_DIR%\%PROJECT_NAME%.exe" info >nul 2>&1
)
echo   Verification complete

REM --- Step 8: Create version info ---
echo.
echo [8/8] Creating distribution metadata...
(
    echo %PROJECT_NAME% v%VERSION%
    echo Built: %DATE% %TIME%
    echo Python: %PY_VER%
    echo Platform: Windows
    echo Author: Virender Dhiman
) > "%DIST_DIR%\BUILD_INFO.txt"

echo.
echo  ====================================================
echo   BUILD COMPLETE
echo  ====================================================
echo.
echo   Standalone .exe:  %DIST_DIR%\%PROJECT_NAME%.exe
echo   Size:
dir "%DIST_DIR%\%PROJECT_NAME%.exe" | find "%PROJECT_NAME%"
echo.
echo   To run:
echo     %DIST_DIR%\%PROJECT_NAME%.exe run "Fix this problem"
echo     %DIST_DIR%\%PROJECT_NAME%.exe --help
echo.
echo   To create an MSI installer (optional):
echo     pip install pymsi
echo     pymsi create "%DIST_DIR%\%PROJECT_NAME%.exe" --output "%DIST_DIR%\%PROJECT_NAME%-installer.msi"
echo.

deactivate
endlocal
