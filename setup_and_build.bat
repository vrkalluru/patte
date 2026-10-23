@echo off
cd /d "%~dp0"
echo ===================================================
echo Patte — One-Click Environment Setup ^& App Builder
echo ===================================================

if not exist "venv\Scripts\python.exe" (
    echo [1/4] Creating Python virtual environment...
    python -m venv venv
)

echo [2/4] Installing required dependencies...
venv\Scripts\pip.exe install --upgrade pip
venv\Scripts\pip.exe install -r requirements.txt pyinstaller

if not exist ".env" (
    echo [3/4] Creating default .env configuration...
    copy /Y ".env.example" ".env"
)

echo [4/4] Building Patte.exe and Patte-Setup.exe...
call build.bat

echo.
echo Setup and build finished! Launching Patte...
start "" "dist\Patte\Patte.exe"
