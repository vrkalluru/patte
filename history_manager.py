"""
history_manager.py — Local persistent storage for previous speech-to-text takes.
Saves takes to history.json in the user's project/app directory.
"""

import json
import os
import sys
import time
from datetime import datetime
from typing import List, Dict, Any

if getattr(sys, "frozen", False):
    APP_DIR = os.path.dirname(sys.executable)
else:
    APP_DIR = os.path.dirname(os.path.abspath(__file__))

HISTORY_FILE = os.path.join(APP_DIR, "history.json")


def _load_raw() -> List[Dict[str, Any]]:
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[HistoryManager] Error reading history: {e}", flush=True)
        return []


def _save_raw(data: List[Dict[str, Any]]):
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[HistoryManager] Error saving history: {e}", flush=True)


def add_take(
    text: str,
    raw_text: str,
    mode: str,
    latency_ms: float,
    audio_duration_s: float = 0.0,
    streaming: bool = True
) -> Dict[str, Any]:
    """Record a newly completed dictation take."""
    if not text or not text.strip():
        return {}

    now = datetime.now()
    take_id = f"take_{int(time.time() * 1000)}"
    word_count = len(text.strip().split())

    entry = {
        "id": take_id,
        "text": text.strip(),
        "raw_text": raw_text.strip() if raw_text else text.strip(),
        "mode": mode,
        "streaming": streaming,
        "latency_ms": round(latency_ms, 1),
        "audio_duration_s": round(audio_duration_s, 2),
        "word_count": word_count,
        "timestamp": now.isoformat(),
        "display_time": now.strftime("%I:%M %p"),
        "display_date": now.strftime("%b %d, %Y"),
    }

    history = _load_raw()
    history.insert(0, entry)

    if len(history) > 200:
        history = history[:200]

    _save_raw(history)
    return entry


def get_takes(limit: int = 100) -> List[Dict[str, Any]]:
    """Retrieve takes ordered newest first."""
    return _load_raw()[:limit]


def delete_take(take_id: str) -> bool:
    """Delete a single take by ID."""
    history = _load_raw()
    new_history = [t for t in history if t.get("id") != take_id]
    if len(new_history) != len(history):
        _save_raw(new_history)
        return True
    return False


def clear_history() -> bool:
    """Clear all stored takes."""
    _save_raw([])
    return True
