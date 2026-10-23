@echo off
cd /d "%~dp0"
echo ============================================================
echo [Patte] 1-Click Fast Rebuild, Deploy, and Diagnostic Launch
echo ============================================================

:: 1. Force kill any existing background or orphaned instances
echo [1/4] Stopping existing Patte processes...
taskkill /F /IM Patte.exe /T >nul 2>&1

:: 2. Fast compile via PyInstaller
echo [2/4] Compiling standalone executable...
venv\Scripts\pyinstaller.exe -y --distpath dist --workpath build whisprflow.spec
if errorlevel 1 (
    echo [ERROR] Build failed! Check compiler output above.
    pause
    exit /b 1
)

:: 3. Deploy binaries to installed location and update shortcuts
echo [3/4] Deploying to %LOCALAPPDATA%\Programs\Patte...
if not exist "%LOCALAPPDATA%\Programs\Patte" mkdir "%LOCALAPPDATA%\Programs\Patte"
xcopy /E /I /Y /Q "dist\Patte\*" "%LOCALAPPDATA%\Programs\Patte\" >nul
powershell -ExecutionPolicy Bypass -File create_shortcuts.ps1 >nul 2>&1

:: 4. Diagnostic launch & immediate check
echo [4/4] Launching and verifying process...
start "" "%LOCALAPPDATA%\Programs\Patte\Patte.exe"
ping 127.0.0.1 -n 3 >nul

powershell -Command "$p = Get-Process -Name Patte -ErrorAction SilentlyContinue; if ($p) { Write-Host '[SUCCESS] Patte is running (PID: ' $p.Id ')' -ForegroundColor Green } else { Write-Host '[FAIL] Patte exited immediately. Recent log output:' -ForegroundColor Red; Get-Content \"$env:LOCALAPPDATA\Programs\Patte\patte.log\" -Tail 15 }"

echo ============================================================
echo Done!
