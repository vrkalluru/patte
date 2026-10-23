# Developer & Agent Debugging Workflow Guide

This document defines the single-command workflows for debugging, rebuilding, and deploying Patte to prevent repetitive exploratory loops.

---

## ⚡ The Single-Command Rebuild & Run

Whenever code changes are made in `main.py`, `config.py`, `refiner.py`, or `gui/`, run:

```cmd
dev_reload.bat
```

### What `dev_reload.bat` does automatically in one go:
1. **Kills lingering instances:** Runs `taskkill /F /IM Patte.exe /T` so file locks on `Patte.exe` are released.
2. **Builds:** Compiles via `venv\Scripts\pyinstaller.exe whisprflow.spec`.
3. **Deploys:** Copies `dist\Patte\*` to `%LOCALAPPDATA%\Programs\Patte\` and refreshes shortcuts.
4. **Verifies:** Launches `Patte.exe`, waits 2 seconds, and checks if the process is alive. If it crashed on startup, it prints the exact Python traceback from `patte.log` immediately.

---

## 🔍 Single-Command Diagnostics

If the app isn't behaving as expected or you want to inspect what's happening without guessing:

### 1. View Live / Recent Logs
```powershell
Get-Content "$env:LOCALAPPDATA\Programs\Patte\patte.log" -Tail 30
```

### 2. Check if Patte is Running
```powershell
Get-Process -Name Patte -ErrorAction SilentlyContinue | Select-Object Id, ProcessName, Path
```

### 3. Direct Console Run (For Instant Python Tracebacks)
If you want to run the code without packaging into PyInstaller:
```powershell
.\venv\Scripts\python.exe main.py
```
*(All `stdout` and `stderr` are mirrored to `patte.log`).*

---

## ⚠️ Known Gotchas & Architecture Rules

1. **Working Directory & Asset Paths:**
   - When compiled, `__file__` in submodules points inside `_internal/gui/`. Always resolve asset paths dynamically across `base_dir/assets`, `sys.executable/assets`, and `sys.executable/_internal/assets`.
2. **System Tray Visibility:**
   - On Windows, if `QSystemTrayIcon` fails to load a valid icon file, Windows hides the icon completely rather than throwing an error. Always ensure icons resolve to a real file.
3. **Single Instance Mutex:**
   - Do not rely on persistent global named mutexes that crash silently on exit; let the application launch and check running processes cleanly.
