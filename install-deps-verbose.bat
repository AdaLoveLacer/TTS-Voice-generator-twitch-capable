@echo off
REM Install dependencies with verbose output and local cache
REM Usage: install-deps-verbose.bat

setlocal enabledelayedexpansion

echo.
echo ════════════════════════════════════════════════════════════════
echo Installing dependencies with VERBOSE output (-vv)
echo Cache directory: .pip_cache (local to project)
echo ════════════════════════════════════════════════════════════════
echo.

REM Get the directory where this script is located
set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

REM Activate virtual environment
echo [1/3] Activating virtual environment...
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    exit /b 1
)

echo [2/3] Installing requirements with verbose output...
echo Pip version:
pip --version
echo.

REM Install with cache and verbose
pip install --cache-dir ".pip_cache" -vv -r xtts-server\requirements.txt

if errorlevel 1 (
    echo.
    echo ERROR: Installation failed
    exit /b 1
)

echo.
echo ════════════════════════════════════════════════════════════════
echo [3/3] Installation complete!
echo ════════════════════════════════════════════════════════════════
echo.

endlocal
