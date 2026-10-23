# 🎙️ Patte — Local AI Voice Dictation for Windows

**Patte** is a fast, privacy-first Windows desktop voice dictation application inspired by Wispr Flow and Superwhisper. Hold **`Ctrl + Space`** in any application, speak naturally (complete with stumbles, filler words, or mid-sentence course corrections), and release—Patte transcribes your speech via a native C++ Whisper engine (`CTranslate2`), normalizes it through an AI endpoint (local or network-hosted), and streams the clean text directly into your active cursor window in under a second.

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
  - **🛡️ 100% Resilient:** If your AI server URL is unreachable, offline, or returns 0 tokens, Patte **never breaks or hangs**—it automatically stops at speech-to-text and outputs the raw Whisper transcription immediately.
- **🌐 Configurable AI Endpoint with Live Connection Test:**
  - Enter any OpenAI-compatible API URL in the Settings tab (e.g. `http://127.0.0.1:1234`, `http://127.0.0.1:11434`, or a network IP like `http://192.168.1.50:11434`).
  - Test the connection directly with the in-app **⚡ Test Connection** button.
- **⌨️ Configurable Text Output Injection:**
  - **Live Keystroke Streaming (`Win32 SendInput`):** Types tokens character-by-character into the focused window in real time as the LLM generates them—without touching your clipboard.
  - **Instant Clipboard Paste (`Ctrl+V`):** Pastes the completed text all at once and automatically restores your previous clipboard contents.
- **🪶 Ultra-Minimal UX & Takes History Timeline:**
  - **28px Non-Activating Micro-Pill:** Appears unobtrusively at the bottom of your screen while listening/polishing, never steals window focus, and vanishes the exact millisecond typing completes.
  - **Obsidian Fluent Dark Dashboard:** Searchable timeline of past takes (with latency badges, word counts, one-click copy, and delete), plus live engine & model settings.
- **📦 Zero-Python Standalone Installation:**
  - Pre-packaged installer bundles the entire Python, Qt6, and AI engine runtime. Runs out of the box on Windows 10/11 without needing Python or developer tools.

---

## 🚀 Quick Installation (For End Users)

1. Download **`Patte-Setup.exe`** from [GitHub Releases](https://github.com/vrkalluru/patte/releases).
2. Run **`Patte-Setup.exe`** and click **OK**.
3. Patte will install to `%LOCALAPPDATA%\Programs\Patte`, add Desktop and Start Menu shortcuts, and launch in your System Tray.

---

## 🎮 How to Use

1. **Place your cursor** in any text field (VS Code, Chrome, Slack, Notion, Discord, Notepad, etc.).
2. **Press and hold `Ctrl + Space`** — a minimal `● Listening...` micro-pill appears at the bottom of your screen.
3. **Speak naturally**, then **release `Ctrl + Space`**.
4. Patte transcribes (and normalizes if an AI server is reached), then streams the text directly into your active window.

---

## 📚 Documentation

- 📖 **[Installation & Setup Instructions (`INSTRUCTIONS.md`)](INSTRUCTIONS.md)** — Step-by-step setup, network endpoint configuration, and troubleshooting.
- 🏗️ **[System Architecture & Engineering Reference (`ARCHITECTURE.md`)](ARCHITECTURE.md)** — Deep dive into the audio pipeline, thread safety (`WhisperDedicatedThread`), Win32 `WH_KEYBOARD_LL` hook filtering, SSE streaming, and latency benchmarks.
- 🛠️ **[Developer & Debugging Guide (`DEBUGGING.md`)](DEBUGGING.md)** — Single-command rebuild workflows (`dev_reload.bat`) and diagnostic commands.

---

## 📄 License
MIT License — Free for personal and commercial use.
