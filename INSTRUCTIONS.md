# 📖 Patte — Installation, Setup & Usage Instructions

This guide walks you through installing **Patte**, configuring the AI refinement API endpoint (local or network-hosted), and troubleshooting.

---

## 1. Prerequisites & Required Tools

To run **Patte** on a new Windows 10 or Windows 11 machine:

### Microsoft Visual C++ Redistributable (x64)
Patte's native C++ Whisper engine (`CTranslate2`) uses OpenMP (`VCOMP140.dll`, `MSVCP140.dll`) for multi-core CPU acceleration.
- **Download:** [https://aka.ms/vs/17/release/vc_redist.x64.exe](https://aka.ms/vs/17/release/vc_redist.x64.exe)
- Or install via PowerShell (`winget`):
  ```powershell
  winget install --id Microsoft.VCRedist.2015+.x64 -e
  ```

---

## 2. Installing Patte

### Method 1: Using the Windows Installer (`Patte-Setup.exe`)
1. Run **`Patte-Setup.exe`** (found in `dist/Patte-Setup.exe` or GitHub Releases).
2. The installer automatically:
   - Copies application binaries to `%LOCALAPPDATA%\Programs\Patte`
   - Creates the **Patte** shortcut on your **Desktop** and in the **Windows Start Menu**
   - Registers **Patte** in **Windows Settings $\rightarrow$ Installed Apps** with a clean uninstaller
   - Launches **Patte** in your Windows System Tray.

### Method 2: Running / Building from Source (Developers)
```powershell
# 1. Automated fast build and launch script
.\dev_reload.bat
```

---

## 3. Configuring the AI Model API Endpoint

Open Patte $\rightarrow$ switch to the **Engine & Settings** tab:

1. **AI API URL**: Enter your OpenAI-compatible completions endpoint:
   - Localhost (e.g., LM Studio): `http://127.0.0.1:1234`
   - Localhost (e.g., Ollama): `http://127.0.0.1:11434`
   - Remote / Local Network IP: `http://192.168.1.50:11434`
2. **Model Name**: The model identifier (e.g., `s1-mini` or `llama3.2`).
3. **Automatic Fallback Safety**:
   - If the endpoint is offline, unreachable, or has an invalid address, Patte **will never crash or hang**.
   - It will automatically stop right at speech-to-text and output your clean, transcribed text directly into your focused cursor window.

---

## 4. How to Use

1. **Hotkey:** Press and hold **`Ctrl + Space`** anywhere in Windows.
2. **Speak:** A subtle `● Listening...` pill will appear at the bottom of the screen.
3. **Release:** Release `Ctrl + Space` to transcribe and insert text instantly.
4. **Dashboard:** Click the microphone tray icon in your Windows taskbar clock area to open the dashboard, review past takes, or change settings.
