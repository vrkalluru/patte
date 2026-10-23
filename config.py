"""
config.py — Configuration loading and persistence for WhisprFlow.
Reads settings from a .env file in the project root.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# Whisper STT model size: tiny.en, base, base.en, small, medium, large-v2
WHISPER_MODEL: str = os.getenv("WHISPER_MODEL", "tiny.en")

# Whisper compute type: int8 (CPU-friendly), float16 (GPU), float32
WHISPER_COMPUTE_TYPE: str = os.getenv("WHISPER_COMPUTE_TYPE", "int8")

# Whisper device: cpu or cuda
WHISPER_DEVICE: str = os.getenv("WHISPER_DEVICE", "cpu")

# Whisper language: "en" (skips language detection pass — 2x faster) or "auto"
WHISPER_LANGUAGE: str = os.getenv("WHISPER_LANGUAGE", "en")

# AI Refinement Provider: lmstudio | groq | openai
AI_PROVIDER: str = os.getenv("AI_PROVIDER", "lmstudio").lower()

# LM Studio local server settings (OpenAI-compatible API)
LM_STUDIO_URL: str = os.getenv("LM_STUDIO_URL", "http://127.0.0.1:1234").replace("localhost", "127.0.0.1")
LM_STUDIO_MODEL: str = os.getenv("LM_STUDIO_MODEL", "s1-mini")

# Cloud Providers (for blazing fast ~200ms latency)
GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# Whether to apply AI refinement after transcription
AI_REFINEMENT_ENABLED: bool = os.getenv("AI_REFINEMENT_ENABLED", "true").lower() == "true"

# Output Injection Mode: True = Live Keystroke Streaming, False = Instant Clipboard Paste
STREAMING_OUTPUT_ENABLED: bool = os.getenv("STREAMING_OUTPUT_ENABLED", "true").lower() == "true"

# Audio settings
SAMPLE_RATE: int = 16000   # Hz — optimal for Whisper
CHANNELS: int = 1          # Mono
DTYPE: str = "float32"     # Direct float32 for faster-whisper


def update_env_setting(key: str, value: str):
    """Update a key=value setting in .env file and in runtime memory."""
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    lines = []
    found = False

    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

    new_lines = []
    for line in lines:
        if line.strip().startswith(f"{key}="):
            new_lines.append(f"{key}={value}\n")
            found = True
        else:
            new_lines.append(line)

    if not found:
        new_lines.append(f"{key}={value}\n")

    with open(env_path, "w", encoding="utf-8") as f:
        f.writelines(new_lines)

    # Update in current os.environ and module global
    os.environ[key] = value
    globals()[key] = value.lower() == "true" if value.lower() in ("true", "false") else value
