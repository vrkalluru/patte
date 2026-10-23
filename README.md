# 🎙️ Patte — Local AI Voice Dictation for Windows

**Patte** is a fast, privacy-first Windows desktop voice dictation application inspired by Wispr Flow and Superwhisper. Hold **`Ctrl + Space`** in any application, speak naturally (complete with stumbles, filler words, or mid-sentence course corrections), and release—Patte transcribes your speech via a native C++ Whisper engine (`CTranslate2`), refines it through an AI endpoint (local or network-hosted), and streams the clean text directly into your active cursor window in under a second.

---

## ✨ Key Features

- **⚡ Sub-Second End-to-End Speed (~0.87s Time-to-First-Word):**
  - Powered by native C++ **`faster-whisper` (`CTranslate2` `int8`)** with persistent HTTP keep-alive and real-time Server-Sent Events (SSE) token streaming.
- **🧠 Surgical Speech Normalization (Smart Mode):**
  - **Course Correction:** Say *"Let's meet at 5, actually scratch that, make it 6"* $\rightarrow$ outputs **`"Let's meet at 6."`**
  - **Filler Removal:** Automatically strips *"um"*, *"uh"*, *"like"*, and *"you know"* without paraphrasing or changing your authentic vocabulary.
  - **Intent-Based List Formatting:** Dictating 3+ enumerable items automatically formats into clean numbered/bulleted lists.
- **⚡ Dual Dictation Modes & Graceful Offline Fallback:**
  - **🧠 Smart Mode:** Whisper C++ ASR + AI server refinement.
  - **⚡ Fast Mode:** Pure Whisper C++ ASR (~450ms latency, zero LLM step).
  - **🛡️ Resilient:** If your AI server URL is unreachable or down, Patte **never breaks or hangs**—it automatically stops at speech-to-text and outputs the raw Whisper transcription immediately.
- **🌐 Flexible AI Endpoint Configuration:**
  - Enter any OpenAI-compatible API URL in the Settings tab (e.g. `http://127.0.0.1:1234`, `http://127.0.0.1:11434`, or a network IP like `http://192.168.1.50:11434`).
- **⌨️ Configurable Text Output Injection:**
  - **Live Keystroke Streaming (`Win32 SendInput`):** Types tokens character-by-character into the focused window in real time as the LLM generates them—without touching your clipboard.
  - **Instant Clipboard Paste (`Ctrl+V`):** Pastes the completed text all at once and automatically restores your previous clipboard contents.
- **🪶 Ultra-Minimal UX & Takes History Timeline:**
  - **28px Non-Activating Micro-Pill:** Appears unobtrusively at the bottom of your screen while listening/polishing, never steals window focus, and vanishes the exact millisecond typing completes.
  - **Obsidian Fluent Dark Dashboard:** Searchable timeline of past takes (with latency badges, word counts, one-click copy, and delete), plus live engine & model settings.

---

## 🚀 Quick Installation (For End Users)

You can install **Patte** either as a standard Windows application (`Patte-Setup.exe`) or from source.

### Step 1: Configure Your AI Server (Optional for Smart Mode)
For AI refinement / smart transcript normalization, Patte connects to any OpenAI-compatible completions endpoint:
- **Localhost:** Run your local server (e.g., `http://127.0.0.1:1234` or `http://127.0.0.1:11434`).
- **Local Network / Remote:** Run your model server on another machine in your network (e.g., `http://192.168.1.50:11434`).
- **Configure in App:** Simply open Patte's **Engine & Settings** tab and provide your **AI Server URL** and **Model Name**.
- *Note:* If no server is running or reachable, Patte gracefully stops at Whisper transcription and outputs your text directly.

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
5. Patte transcribes (and polishes if an AI server is reached), then streams the text directly into your active window.

---

## 📚 Documentation

- 📖 **[Step-by-Step User & Setup Instructions (`INSTRUCTIONS.md`)](INSTRUCTIONS.md)** — Detailed setup and configuration options.
- 🏗️ **[System Architecture & Engineering Guide (`ARCHITECTURE.md`)](ARCHITECTURE.md)** — Deep dive into the audio pipeline, thread safety (`WhisperDedicatedThread`), Win32 `WH_KEYBOARD_LL` hook filtering, SSE streaming, and latency benchmarks.

---

## 📄 License
MIT License — Free for personal and commercial use.
