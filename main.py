# -*- coding: utf-8 -*-
"""
main.py — Patte Windows Desktop Application.
Modern PyQt6 interface with micro-pill overlay, instant Fast/Smart mode toggle,
single-instance mutex protection, dedicated Whisper worker thread, configurable
streaming output, and persistent takes timeline.
"""

import os
import sys
import time
import ctypes
import threading
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QObject, pyqtSignal

if getattr(sys, "frozen", False):
    APP_DIR = os.path.dirname(sys.executable)
else:
    APP_DIR = os.path.dirname(os.path.abspath(__file__))

# Always route stdout/stderr to patte.log so logs are captured even when console=False
LOG_FILE_PATH = os.path.join(APP_DIR, "patte.log")
try:
    _log_file = open(LOG_FILE_PATH, "a", encoding="utf-8", buffering=1)
    sys.stdout = _log_file
    sys.stderr = _log_file
except Exception:
    pass

import config
from recorder import Recorder
from transcriber import transcribe
from refiner import refine, refine_stream, prewarm_refiner
from paster import paste_text, prepare_for_typing, type_token
from hotkey import HotkeyListener
from gui.main_window import MainWindow


class PipelineBridge(QObject):
    """Thread-safe signal bridge between background audio threads and PyQt GUI."""

    sig_recording_started = pyqtSignal()
    sig_recording_stopped = pyqtSignal()
    sig_transcribing = pyqtSignal()
    sig_refining = pyqtSignal()
    sig_pasted = pyqtSignal(str)
    sig_new_take = pyqtSignal(str, str, float)
    sig_status_msg = pyqtSignal(str)


class PatteApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setApplicationName("Patte")
        self.app.setQuitOnLastWindowClosed(False)  # Keep running in system tray

        self.bridge = PipelineBridge()
        self.window = MainWindow()
        self.recorder = Recorder()
        self._processing_lock = threading.Lock()

        self._connect_signals()
        self._start_hotkey_listener()
        self._prewarm_whisper()

    def _connect_signals(self):
        self.bridge.sig_recording_started.connect(self.window.set_status_recording)
        self.bridge.sig_transcribing.connect(self.window.set_status_transcribing)
        self.bridge.sig_refining.connect(self.window.set_status_refining)
        self.bridge.sig_pasted.connect(self.window.set_status_pasted)
        self.bridge.sig_new_take.connect(self.window.add_new_take)
        self.bridge.sig_status_msg.connect(self.window.set_status_idle_with_msg)

    def _start_hotkey_listener(self):
        self.hotkey = HotkeyListener(
            on_activate=self._on_hotkey_down,
            on_deactivate=self._on_hotkey_up,
        )
        self.hotkey.start()

    def _prewarm_whisper(self):
        """Pre-warm Whisper C++ model and S1-Mini KV cache on startup."""
        def load_model():
            try:
                from transcriber import _get_model
                _get_model()
                print("[Patte] Whisper model pre-warmed and ready.", flush=True)
                prewarm_refiner()
            except Exception as e:
                print(f"[Patte] Model prewarm error: {e}", flush=True)

        threading.Thread(target=load_model, daemon=True).start()

    def _on_hotkey_down(self):
        """Called when Ctrl+Space is pressed down."""
        print("[Patte] >> Hotkey pressed: Recording started.", flush=True)
        self.bridge.sig_recording_started.emit()
        self.recorder.start()

    def _on_hotkey_up(self):
        """Called when Ctrl+Space is released."""
        if not self._processing_lock.acquire(blocking=False):
            print("[Patte] Already processing an audio block, ignoring.", flush=True)
            return

        def process_job():
            t_keyup = time.perf_counter()
            try:
                print("[Patte] -- Hotkey released: Processing audio...", flush=True)
                audio_data = self.recorder.stop()

                if audio_data is None:
                    print("[Patte] Audio too short or silent.", flush=True)
                    self.bridge.sig_status_msg.emit("Hold longer to speak")
                    return

                # ── Transcribe on Dedicated Whisper Worker Thread ─────────────
                self.bridge.sig_transcribing.emit()
                t_w0 = time.perf_counter()
                raw_text = transcribe(audio_data)
                whisper_ms = (time.perf_counter() - t_w0) * 1000

                if not raw_text:
                    print("[Patte] No speech detected.", flush=True)
                    self.bridge.sig_status_msg.emit("No speech detected")
                    return

                print(f"[Patte] RAW ({whisper_ms:.0f}ms ASR): {raw_text}", flush=True)

                # ── Refine & Output ───────────────────────────────────────────
                if config.AI_REFINEMENT_ENABLED:
                    self.bridge.sig_refining.emit()
                    t_llm0 = time.perf_counter()

                    if config.STREAMING_OUTPUT_ENABLED:
                        # Mode 1: Live Real-Time Keystroke Injection
                        prepare_for_typing()
                        first_token_ms = None

                        def on_stream_token(tok: str):
                            nonlocal first_token_ms
                            if first_token_ms is None:
                                first_token_ms = (time.perf_counter() - t_llm0) * 1000
                            type_token(tok)

                        final_text = refine_stream(raw_text, on_token=on_stream_token)
                        llm_total_ms = (time.perf_counter() - t_llm0) * 1000
                        total_keyup_ms = (time.perf_counter() - t_keyup) * 1000
                        ttft_val = first_token_ms if first_token_ms is not None else llm_total_ms
                        print(
                            f"[Timing] Stream Mode — Whisper: {whisper_ms:.0f}ms | "
                            f"LLM TTFT: {ttft_val:.0f}ms | Total: {total_keyup_ms:.0f}ms",
                            flush=True,
                        )
                    else:
                        # Mode 2: Wait & Paste via Clipboard
                        final_text = refine(raw_text)
                        paste_text(final_text)
                        total_keyup_ms = (time.perf_counter() - t_keyup) * 1000
                        print(
                            f"[Timing] Paste Mode — Whisper: {whisper_ms:.0f}ms | Total: {total_keyup_ms:.0f}ms",
                            flush=True,
                        )
                else:
                    final_text = raw_text
                    paste_text(final_text)
                    total_keyup_ms = (time.perf_counter() - t_keyup) * 1000
                    print(
                        f"[Timing] Fast Mode — Whisper: {whisper_ms:.0f}ms | Total: {total_keyup_ms:.0f}ms",
                        flush=True,
                    )

                # Update UI & Append to History
                self.bridge.sig_pasted.emit(final_text)
                self.bridge.sig_new_take.emit(final_text, raw_text, total_keyup_ms)
                print(f"[Patte] Done: {final_text!r}", flush=True)

            except Exception as e:
                print(f"[Patte] Pipeline exception: {e}", flush=True)
                import traceback
                traceback.print_exc()
                self.bridge.sig_status_msg.emit("Error during transcription")

            finally:
                self._processing_lock.release()

        threading.Thread(target=process_job, daemon=True).start()

    def run(self):
        self.window.show()
        return self.app.exec()


def main():
    # Enforce single running instance via Windows Named Mutex
    kernel32 = ctypes.windll.kernel32
    mutex = kernel32.CreateMutexW(None, False, "Local\\PatteVoiceAppSingleInstanceMutex")
    if kernel32.GetLastError() == 183:  # ERROR_ALREADY_EXISTS
        print("[Patte] Another instance is already running; bringing window to front and exiting duplicate.", flush=True)
        user32 = ctypes.windll.user32
        hwnd = user32.FindWindowW(None, "Patte")
        if hwnd:
            user32.ShowWindow(hwnd, 9)  # SW_RESTORE
            user32.SetForegroundWindow(hwnd)
        sys.exit(0)

    app = PatteApp()
    sys.exit(app.run())


if __name__ == "__main__":
    main()
