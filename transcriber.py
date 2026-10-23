"""
transcriber.py — Local speech-to-text via faster-whisper (CTranslate2 C++ engine).
Uses a single dedicated immortal worker thread for all CTranslate2 OpenMP calls
to prevent MSVC OpenMP (VCOMP140.dll) thread-local storage access violations (0xc0000005).
"""

import queue
import threading
from typing import Optional
import numpy as np
import config

_job_queue: "queue.Queue[tuple[Optional[np.ndarray], queue.Queue]]" = queue.Queue()
_worker_started = False
_worker_lock = threading.Lock()

# Common Whisper hallucinations on quiet/silent audio
_SILENCE_HALLUCINATIONS = {
    "bye.", "bye-bye.", "bye bye.", "thank you.", "thanks for watching.",
    "you", "thank you for watching.", "subtitles by", "amara.org"
}


def _whisper_worker_loop():
    """Dedicated single OS thread that owns the CTranslate2 model and OpenMP thread pool."""
    from faster_whisper import WhisperModel

    current_model_name = None
    model = None

    while True:
        audio_array, result_q = _job_queue.get()
        try:
            if model is None or current_model_name != config.WHISPER_MODEL:
                current_model_name = config.WHISPER_MODEL
                print(
                    f"[Transcriber] Loading Whisper model '{current_model_name}' "
                    f"on {config.WHISPER_DEVICE} with {config.WHISPER_COMPUTE_TYPE} (4 threads)...",
                    flush=True,
                )
                model = WhisperModel(
                    current_model_name,
                    device=config.WHISPER_DEVICE,
                    compute_type=config.WHISPER_COMPUTE_TYPE,
                    cpu_threads=4,
                )
                # Warm up OpenMP thread pool on this dedicated thread
                dummy = np.zeros(8000, dtype=np.float32)
                segs, _ = model.transcribe(dummy, beam_size=1, language="en", without_timestamps=True)
                list(segs)
                print("[Transcriber] Model loaded and pre-warmed on dedicated thread.", flush=True)

            if audio_array is None:
                # Pre-warm only request
                result_q.put(None)
                continue

            lang = None if config.WHISPER_LANGUAGE.lower() == "auto" else config.WHISPER_LANGUAGE

            segments, _ = model.transcribe(
                audio_array,
                beam_size=1,
                best_of=1,
                temperature=0.0,
                condition_on_previous_text=False,
                without_timestamps=True,
                language=lang,
                vad_filter=False,
                no_speech_threshold=0.6,
            )

            parts = [seg.text.strip() for seg in segments if seg.text.strip()]
            raw_text = " ".join(parts).strip()

            if not raw_text:
                result_q.put(None)
                continue

            # Guard against single-word silence hallucinations on low-energy audio
            rms = float(np.sqrt(np.mean(audio_array * audio_array)))
            if rms < 0.015 and raw_text.lower() in _SILENCE_HALLUCINATIONS:
                print(f"[Transcriber] Filtered low-energy silence hallucination: {raw_text!r}", flush=True)
                result_q.put(None)
                continue

            print(f"[Transcriber] Raw text: {raw_text!r}", flush=True)
            result_q.put(raw_text)

        except Exception as e:
            print(f"[Transcriber] Worker error: {e}", flush=True)
            result_q.put(None)


def _ensure_worker():
    global _worker_started
    with _worker_lock:
        if not _worker_started:
            t = threading.Thread(target=_whisper_worker_loop, name="WhisperDedicatedThread", daemon=True)
            t.start()
            _worker_started = True


def _get_model():
    """Pre-warm the dedicated Whisper worker thread."""
    _ensure_worker()
    res_q: queue.Queue = queue.Queue()
    _job_queue.put((None, res_q))
    res_q.get()


def transcribe(audio_array: np.ndarray) -> Optional[str]:
    """
    Transcribe audio (16kHz float32 numpy array) to text on the dedicated Whisper thread.
    Supports arbitrary length audio safely.
    """
    _ensure_worker()
    res_q: queue.Queue = queue.Queue()
    _job_queue.put((audio_array, res_q))
    return res_q.get()
