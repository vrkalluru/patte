@echo off
cd /d "%~dp0"
echo ===================================================
echo Building Patte Standalone App and Windows Installer
echo ===================================================

taskkill /F /IM Patte.exe /T >nul 2>&1

echo [1/3] Compiling standalone Patte.exe via PyInstaller...
venv\Scripts\pyinstaller.exe -y --distpath dist --workpath build whisprflow.spec

if exist "dist\Patte\Patte.exe" (
    copy /Y ".env" "dist\Patte\.env" >nul 2>&1
    if not exist "dist\Patte\.env" copy /Y ".env.example" "dist\Patte\.env" >nul 2>&1
    if exist "history.json" copy /Y "history.json" "dist\Patte\history.json" >nul 2>&1

    echo [2/3] Compiling Patte-Setup.exe Windows Installer...
    venv\Scripts\pyinstaller.exe -y --onefile --noconsole --name "Patte-Setup" --icon "assets\icon.ico" --distpath dist --workpath build installer_setup.py

    echo [3/3] Updating Desktop and Start Menu shortcuts...
    venv\Scripts\python.exe create_shortcut.py

    echo.
    echo [SUCCESS] Build Complete!
    echo   - Standalone App : dist\Patte\Patte.exe
    echo   - Setup Installer: dist\Patte-Setup.exe
) else (
    echo [ERROR] Build failed. Check the logs above.
)
