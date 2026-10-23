"""
recorder.py — Microphone audio recording for Patte.
Uses sounddevice callback-based recording at 16kHz mono float32.
Safely handles long dictations of any duration with automatic leading/trailing silence trimming.
"""

import threading
import numpy as np
import sounddevice as sd
from typing import Optional
import config


class Recorder:
    """Records audio from the default microphone while active."""

    BLOCK_SIZE = 1024
    SILENCE_RMS_THRESHOLD = 0.006

    def __init__(self):
        self._frames: list[np.ndarray] = []
        self._lock = threading.Lock()
        self._stream_lock = threading.Lock()
        self._stream: Optional[sd.InputStream] = None
        self._recording = False

    @property
    def is_recording(self) -> bool:
        return self._recording

    def _callback(self, indata: np.ndarray, frames: int, time, status):
        """Called by PortAudio on each audio block (64ms)."""
        if self._recording:
            with self._lock:
                self._frames.append(indata.copy())

    def start(self):
        """Begin capturing audio from the default microphone."""
        with self._stream_lock:
            if self._stream is not None:
                try:
                    self._stream.stop()
                    self._stream.close()
                except Exception:
                    pass
                self._stream = None

            with self._lock:
                self._frames = []
            self._recording = True
            self._stream = sd.InputStream(
                samplerate=config.SAMPLE_RATE,
                channels=config.CHANNELS,
                dtype=config.DTYPE,
                callback=self._callback,
                blocksize=self.BLOCK_SIZE,
            )
            self._stream.start()
            print("[Recorder] Recording started.", flush=True)

    def stop(self) -> Optional[np.ndarray]:
        """
        Stop recording and return the captured audio as a 1D float32 numpy array.
        Trims dead leading/trailing silence and returns None if no speech was captured.
        """
        self._recording = False
        with self._stream_lock:
            if self._stream is not None:
                try:
                    self._stream.stop()
                    self._stream.close()
                except Exception as e:
                    print(f"[Recorder] Error closing stream: {e}", flush=True)
                self._stream = None

        with self._lock:
            frames = list(self._frames)
            self._frames = []

        if not frames:
            print("[Recorder] No audio frames captured.", flush=True)
            return None

        # Trim dead leading/trailing silent blocks while keeping a 2-block margin
        non_silent_indices = [
            i for i, blk in enumerate(frames)
            if float(np.sqrt(np.mean(blk * blk))) >= self.SILENCE_RMS_THRESHOLD
        ]

        if not non_silent_indices:
            print("[Recorder] Audio contained only silence, skipping.", flush=True)
            return None

        start_idx = max(0, non_silent_indices[0] - 2)
        end_idx = min(len(frames), non_silent_indices[-1] + 3)
        trimmed_frames = frames[start_idx:end_idx]

        audio = np.concatenate(trimmed_frames, axis=0).flatten().astype(np.float32)

        # Must have at least ~0.25 seconds of active audio
        min_samples = int(config.SAMPLE_RATE * 0.25)
        if len(audio) < min_samples:
            print("[Recorder] Audio too short, skipping.", flush=True)
            return None

        print(f"[Recorder] Captured {len(audio) / config.SAMPLE_RATE:.2f}s of active speech.", flush=True)
        return audio
