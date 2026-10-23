# 📖 Patte — Installation, Setup & Usage Instructions

This guide walks you through installing **Patte**, configuring the AI refinement API endpoint (local or network-hosted), and troubleshooting.

---

## 1. Prerequisites & Required Tools

To run **Patte** on a Windows 10 or Windows 11 machine:

### Microsoft Visual C++ Redistributable (x64)
Patte's native C++ Whisper engine (`CTranslate2`) uses OpenMP (`VCOMP140.dll`, `MSVCP140.dll`) for multi-core CPU acceleration.
- **Download:** [https://aka.ms/vs/17/release/vc_redist.x64.exe](https://aka.ms/vs/17/release/vc_redist.x64.exe)
- Or install via PowerShell (`winget`):
  ```powershell
  winget install --id Microsoft.VCRedist.2015+.x64 -e
  ```

> [!NOTE]
> **No Python is required on target machines.** The standalone installer (`Patte-Setup.exe`) bundles all required Python, Qt6, and AI engine runtimes.

---

## 2. Installing Patte

### Method 1: Using the Windows Installer (`Patte-Setup.exe`)
1. Download **`Patte-Setup.exe`** from the [GitHub Releases page](https://github.com/vrkalluru/patte/releases).
2. Double-click **`Patte-Setup.exe`** and click **OK**.
3. The installer automatically:
   - Installs all application files to `%LOCALAPPDATA%\Programs\Patte`
   - Creates a **Desktop** shortcut (`Patte.lnk`) and a **Start Menu** entry
   - Registers **Patte** in **Windows Settings $\rightarrow$ Installed Apps** with a clean uninstaller
   - Launches **Patte** in your Windows System Tray.

### Method 2: Running / Building from Source (Developers)
```powershell
# Automated 1-click fast build, deploy, and launch script
.\dev_reload.bat
```

---

## 3. Configuring the AI Model API Endpoint

Open Patte $\rightarrow$ switch to the **Engine & Settings** tab:

1. **AI API URL**: Enter your OpenAI-compatible completions endpoint:
   - Localhost (e.g., LM Studio): `http://127.0.0.1:1234`
   - Localhost (e.g., Ollama): `http://127.0.0.1:11434`
   - Remote / Local Network IP: `http://192.168.1.50:11434`
2. **Model Name**: The model identifier (e.g., `s1-mini`, `llama3.2`, or your fine-tuned model).
3. **⚡ Test Connection Button**: Click the button directly in settings to test connectivity before speaking.
   - Shows latency upon success: `✓ Connected successfully (85ms latency)`.
   - Reports clear errors if unreachable: `✗ Connection failed: Server is offline`.
4. **Automatic Fallback Safety**:
   - If the endpoint is offline, unreachable, or returns 0 tokens, Patte **will never crash or hang**.
   - It will automatically stop right at speech-to-text and output your clean, transcribed text directly into your focused cursor window.

---

## 4. How to Use

1. **Hotkey:** Press and hold **`Ctrl + Space`** anywhere in Windows.
2. **Speak:** A subtle `● Listening...` pill will appear at the bottom of the screen.
3. **Release:** Release `Ctrl + Space` to transcribe and insert text instantly.
4. **Dashboard:** Click the microphone tray icon in your Windows taskbar clock area (or double-click the Desktop shortcut) to open the dashboard, review past takes, or change settings.
