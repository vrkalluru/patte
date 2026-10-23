# 🎙️ Patte — Local AI Voice Dictation for Windows

**Patte** is a fast, privacy-first Windows desktop voice dictation application inspired by Wispr Flow and Superwhisper. Hold **`Ctrl + Space`** in any application, speak naturally (complete with stumbles, filler words, or mid-sentence course corrections), and release—Patte transcribes your speech via a native C++ Whisper engine (`CTranslate2`), normalizes it through **`superwhisper/s1-mini`**, and streams the clean text directly into your active cursor window in under a second.

---

## ✨ Key Features

- **⚡ Sub-Second End-to-End Speed (~0.87s Time-to-First-Word):**
  - Powered by native C++ **`faster-whisper` (`CTranslate2` `int8`)** + **`superwhisper/s1-mini`** via persistent HTTP keep-alive and real-time Server-Sent Events (SSE) token streaming.
- **🧠 Surgical Speech Normalization (Smart Mode):**
  - **Course Correction:** Say *"Let's meet at 5, actually scratch that, make it 6"* $\rightarrow$ outputs **`"Let's meet at 6."`**
  - **Filler Removal:** Automatically strips *"um"*, *"uh"*, *"like"*, and *"you know"* without paraphrasing or changing your authentic vocabulary.
  - **Intent-Based List Formatting:** Dictating 3+ enumerable items automatically formats into clean numbered/bulleted lists.
- **⚡ Dual Dictation Modes:**
  - **🧠 Smart Mode:** Whisper C++ ASR + S1-Mini AI normalization.
  - **⚡ Fast Mode:** Pure Whisper C++ ASR (~450ms latency, zero LLM step).
- **⌨️ Configurable Text Output Injection:**
  - **Live Keystroke Streaming (`Win32 SendInput`):** Types tokens character-by-character into the focused window in real time as the LLM generates them—without touching your clipboard.
  - **Instant Clipboard Paste (`Ctrl+V`):** Pastes the completed text all at once and automatically restores your previous clipboard contents.
- **🪶 Ultra-Minimal UX & Takes History Timeline:**
  - **28px Non-Activating Micro-Pill:** Appears unobtrusively at the bottom of your screen while listening/polishing, never steals window focus, and vanishes the exact millisecond typing completes.
  - **Obsidian Fluent Dark Dashboard:** Searchable timeline of past takes (with latency badges, word counts, one-click copy, and delete), plus live engine & model settings.

---

## 🚀 Quick Installation (For End Users)

Anyone with this repository can install **Patte** either as a standard Windows application (`Patte-Setup.exe`) or from source.

### Step 1: Install Required AI Runtime (For Smart Mode)
Patte uses **LM Studio** to run the lightweight `superwhisper/s1-mini` (462 MB) speech-normalization model locally on your CPU or GPU:

1. Download and install **[LM Studio](https://lmstudio.ai/)** for Windows.
2. Open a terminal (PowerShell) or search inside LM Studio to download **`superwhisper/s1-mini-GGUF`**:
   ```powershell
   lms get superwhisper/s1-mini-GGUF
   ```
3. Start the LM Studio local server on port `1234` and load `s1-mini`:
   ```powershell
   lms server start
   lms load superwhisper/s1-mini-GGUF --identifier s1-mini
   ```
   *(Note: If LM Studio is not running, Patte will automatically attempt to start it via `lms server start` or gracefully fall back to raw Whisper transcription).*

---

### Step 2: Install Patte (Option A — Windows Installer `.exe`)
1. Run **`Patte-Setup.exe`** (located in `dist/Patte-Setup.exe` or the GitHub Releases page).
2. The installer will:
   - Install Patte to `%LOCALAPPDATA%\Programs\Patte`
   - Create **Desktop** and **Start Menu** shortcuts (`Patte`)
   - Register **Patte** in **Windows Settings $\rightarrow$ Installed Apps (Add or Remove Programs)** with a clean uninstaller
   - Launch **Patte** in your Windows System Tray.

---

### Step 2: Install & Build from Source (Option B — Developers)

#### Prerequisites
- **Windows 10 / 11 (64-bit)**
- **[Python 3.11 or 3.12](https://www.python.org/downloads/windows/)**
- **[Microsoft Visual C++ Redistributable (x64)](https://aka.ms/vs/17/release/vc_redist.x64.exe)** (required by `CTranslate2` for OpenMP `VCOMP140.dll`)

#### 1. Clone the Repository
```powershell
git clone https://github.com/vrkalluru/patte.git
cd patte
```

#### 2. Automated One-Click Setup & Build
Run the included setup script to create the virtual environment, install dependencies, compile `Patte.exe`, and register Windows shortcuts:
```powershell
.\setup_and_build.bat
```

Or run the commands manually:
```powershell
# 1. Create and activate virtual environment
python -m venv venv
.\venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Copy default configuration
copy .env.example .env

# 4. Run directly (or build standalone .exe + installer)
python main.py

# 5. (Optional) Compile standalone Patte.exe and Patte-Setup.exe installer
.\build.bat
```

---

## 🎮 How to Use

1. **Launch Patte** from your Desktop or Start Menu shortcut. It sits quietly in the Windows System Tray.
2. **Place your cursor** in any text field (VS Code, Chrome, Slack, Notion, Discord, Notepad, etc.).
3. **Press and hold `Ctrl + Space`** — a minimal `● Listening` micro-pill appears at the bottom of your screen.
4. **Speak naturally**, then **release `Ctrl + Space`**.
5. Patte transcribes, polishes, and streams the text directly into your active window, then immediately dismisses the micro-pill.

---

## 📚 Documentation

- 📖 **[Step-by-Step User & Setup Instructions (`INSTRUCTIONS.md`)](INSTRUCTIONS.md)** — Detailed setup, LM Studio configuration, cloud provider setup (Groq/OpenAI), and troubleshooting.
- 🏗️ **[System Architecture & Engineering Guide (`ARCHITECTURE.md`)](ARCHITECTURE.md)** — Deep dive into the audio pipeline, thread safety (`WhisperDedicatedThread`), Win32 `WH_KEYBOARD_LL` hook filtering, SSE streaming, and latency benchmarks.

---

## 📄 License
MIT License — Free for personal and commercial use.
