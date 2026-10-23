# 📖 Patte — Complete Installation, Setup & Usage Instructions

This guide walks you through installing **Patte**, setting up the local AI refinement model (`superwhisper/s1-mini`), configuring cloud alternatives (Groq / OpenAI), and troubleshooting common Windows issues.

---

## 1. Prerequisites & Required Tools

To run **Patte** on a new Windows 10 or Windows 11 machine, install the following tools:

### A. Microsoft Visual C++ Redistributable (x64)
Patte's native C++ Whisper engine (`CTranslate2`) uses OpenMP (`VCOMP140.dll`, `MSVCP140.dll`) for multi-core CPU acceleration.
- **Download:** [https://aka.ms/vs/17/release/vc_redist.x64.exe](https://aka.ms/vs/17/release/vc_redist.x64.exe)
- Or install via PowerShell (`winget`):
  ```powershell
  winget install --id Microsoft.VCRedist.2015+.x64 -e
  ```

### B. LM Studio (For Local Smart Mode AI Refinement)
In **Smart Mode**, Patte connects to a local OpenAI-compatible server (`http://127.0.0.1:1234/v1/chat/completions`) running **`superwhisper/s1-mini-GGUF`** (~462 MB)—an ultra-fast 0.6B model purpose-built for cleaning speech transcripts.
1. Install **[LM Studio](https://lmstudio.ai/)** (or run `winget install --id ElementLabs.LMStudio -e`).
2. Download the **`superwhisper/s1-mini-GGUF`** model via PowerShell:
   ```powershell
   lms get superwhisper/s1-mini-GGUF
   ```
   *(Alternatively, open LM Studio $\rightarrow$ click the **Discover / Search** tab $\rightarrow$ search `superwhisper/s1-mini-GGUF` $\rightarrow$ download `s1-mini-q4_k_m.gguf`).*
3. Load the model and start the local server on port `1234`:
   ```powershell
   lms server start
   lms load superwhisper/s1-mini-GGUF --identifier s1-mini
   ```

### C. Python 3.11 / 3.12 (Only required if building from source)
If you are running the pre-built **`Patte-Setup.exe`** installer, Python is **not** required. If building from source:
```powershell
winget install --id Python.Python.3.12 -e
```

---

## 2. Installing Patte

### Method 1: Using the Windows Installer (`Patte-Setup.exe`)
1. Double-click **`Patte-Setup.exe`** (found in `dist/Patte-Setup.exe` or on the GitHub Releases page).
2. Click **Install Patte**.
3. The installer automatically:
   - Extracts all application binaries to `%LOCALAPPDATA%\Programs\Patte`
   - Creates the **Patte** shortcut on your **Desktop** and in the **Windows Start Menu**
   - Registers **Patte** in **Windows Settings $\rightarrow$ Apps $\rightarrow$ Installed Apps** (with a one-click Uninstaller)
   - Launches **Patte** in the background.

### Method 2: Building & Installing from Source
1. Open PowerShell in the project folder and run:
   ```powershell
   .\setup_and_build.bat
   ```
2. This script automatically:
   - Creates `venv\` and installs all packages from `requirements.txt`
   - Copies `.env.example` to `.env` if not present
   - Compiles the standalone application (`dist\Patte\Patte.exe`) and Windows installer (`dist\Patte-Setup.exe`)
   - Creates Desktop and Start Menu shortcuts.

---

## 3. Using Patte

### Global Push-to-Talk (`Ctrl + Space`)
1. Click inside **any text box** in any Windows application (browser, IDE, email client, chat app).
2. **Press and hold `Ctrl + Space`**:
   - A tiny 28px micro-pill (`● Listening`) appears at the bottom center of your screen.
3. **Speak naturally**:
   - You can pause, say *"um"* or *"uh"*, or correct yourself mid-sentence (e.g., *"Let's schedule the call for Tuesday, actually scratch that, make it Wednesday at 2 PM"*).
   - You can dictate lists (e.g., *"We need three items: first update the docs, second run unit tests, third push the release"*).
4. **Release `Ctrl + Space`**:
   - The micro-pill switches to `⚡ Processing` $\rightarrow$ `✦ Polishing`, streams the cleaned text directly into your cursor window, and **immediately disappears** the millisecond typing finishes.

---

## 4. Dashboard & Configuration

Click the **Patte soundwave icon** in the Windows System Tray (or open **Patte** from your Desktop shortcut) to access the main dashboard:

### Tab 1: 🎙️ Takes & History
- **Mode Switcher:**
  - **🧠 Smart Mode:** Runs Whisper C++ ASR + S1-Mini transcript normalization (removes fillers, resolves self-corrections, formats lists).
  - **⚡ Fast Mode:** Runs Whisper C++ ASR only (~450ms latency) and pastes the raw transcript directly.
- **Output Mode Toggle:**
  - **⚡ Streaming: Live Keystrokes:** Types tokens in real time as they stream from the LLM using native Win32 `SendInput` (`KEYEVENTF_UNICODE`)—never touches your clipboard.
  - **📋 Output: Clipboard Paste:** Waits for the full sentence, pastes it all at once via `Ctrl+V`, and restores your previous clipboard after 800ms.
- **Takes Timeline:**
  - Every dictation is saved locally in `history.json` with its timestamp, mode badge, latency (`ms`), and word count.
  - Use the search box (`🔍 Search past takes...`) to filter past takes, click **📋 Copy Text** to copy any take, or click **🗑️** to delete individual takes.

### Tab 2: ⚙️ Engine & Settings
- **Whisper Model Size:**
  - `tiny.en` *(Default — ~450ms on CPU, recommended when paired with Smart Mode)*
  - `base.en` *(~850ms on CPU)*
  - `base` *(Multilingual)*
  - `small` *(Higher accuracy for complex technical terms, slower on CPU)*
- **Spoken Language:**
  - `en` *(Default — skips Whisper's language-detection pass, making transcription **2x faster**)*
  - `auto` *(Auto-detects language across 99 languages)*

---

## 5. Optional: Using Groq Cloud for ~150ms 70B Refinement

If your PC does not have a dedicated GPU or you don't want to run LM Studio locally, Patte supports **Groq's LPU Cloud API** (free tier available):
1. Get a free API key at [https://console.groq.com/keys](https://console.groq.com/keys).
2. Open `.env` (located next to `Patte.exe` or in the project root) and set:
   ```ini
   AI_PROVIDER=groq
   GROQ_API_KEY=gsk_your_api_key_here
   GROQ_MODEL=llama-3.3-70b-versatile
   ```
3. Restart Patte.

---

## 6. Troubleshooting

| Symptom | Cause & Solution |
| :--- | :--- |
| **Smart Mode outputs raw unpolished text** | Make sure LM Studio is running with `s1-mini` loaded (`lms server start` and `lms load superwhisper/s1-mini-GGUF --identifier s1-mini`). Check `patte.log` in the app folder for connection details. |
| **Text does not type into an Administrator window (e.g., elevated Task Manager / admin terminal)** | Windows UIPI (User Interface Privilege Isolation) blocks non-elevated apps from sending keystrokes into Administrator windows. Run `Patte.exe` as Administrator if dictating into elevated apps. |
| **First run takes a few seconds to initialize** | On the very first launch, `faster-whisper` downloads the ~75 MB `tiny.en` CTranslate2 model into `%USERPROFILE%\.cache\huggingface\hub\`. All subsequent launches load from disk in <1 second. |
| **Where are logs and history stored?** | Runtime logs are written to `patte.log` and dictation history is stored in `history.json` inside the `Patte` application directory. |
