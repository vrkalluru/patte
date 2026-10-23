"""
hotkey.py — Global hotkey listener for Patte.
Detects Ctrl+Space press (start) and release (stop) globally across all Windows apps.
Uses a fast Win32 low-level event filter to ignore simulated/injected keystrokes (LLKHF_INJECTED)
so streaming long text via SendInput never re-enters pynput's Unicode translation callbacks.
"""

import threading
from typing import Callable
from pynput import keyboard
from pynput.keyboard import Key

LLKHF_INJECTED = 0x00000010
_TARGET_VKS = {17, 162, 163, 32}  # VK_CONTROL, VK_LCONTROL, VK_RCONTROL, VK_SPACE


class HotkeyListener:
    """
    Listens globally for Ctrl+Space hold/release.
    - on_activate: called when Ctrl+Space is pressed (starts recording)
    - on_deactivate: called when either key is released (stops recording)
    """

    def __init__(self, on_activate: Callable, on_deactivate: Callable):
        self._on_activate = on_activate
        self._on_deactivate = on_deactivate
        self._held_keys: set = set()
        self._active = False
        self._listener: keyboard.Listener | None = None
        self._lock = threading.Lock()

    def _win32_event_filter(self, msg, data):
        """
        Low-level Win32 hook filter.
        Returning False tells pynput not to post the event to its internal thread queue
        (while still allowing Windows CallNextHookEx to deliver the key to the active app).
        """
        try:
            if getattr(data, "flags", 0) & LLKHF_INJECTED:
                return False
            vk = getattr(data, "vkCode", 0)
            if vk not in _TARGET_VKS:
                return False
        except Exception:
            pass
        return True

    def _normalize(self, key) -> Key | None:
        """Normalize left/right ctrl variants and space across all Windows keyboard events."""
        if key in (Key.ctrl, Key.ctrl_l, Key.ctrl_r):
            return Key.ctrl_l
        if key == Key.space:
            return Key.space

        vk = getattr(key, "vk", None)
        if vk in (17, 162, 163):
            return Key.ctrl_l
        if vk == 32:
            return Key.space

        if getattr(key, "char", None) == " ":
            return Key.space

        return None

    def _on_press(self, key):
        normalized = self._normalize(key)
        if normalized is None:
            return

        with self._lock:
            self._held_keys.add(normalized)
            combo_held = Key.ctrl_l in self._held_keys and Key.space in self._held_keys

            if combo_held and not self._active:
                self._active = True
                threading.Thread(target=self._on_activate, daemon=True).start()

    def _on_release(self, key):
        normalized = self._normalize(key)
        if normalized is None:
            return

        with self._lock:
            self._held_keys.discard(normalized)
            was_active = self._active

            if was_active and normalized in (Key.ctrl_l, Key.space):
                self._active = False
                threading.Thread(target=self._on_deactivate, daemon=True).start()

    def start(self):
        """Start the global keyboard listener."""
        self._listener = keyboard.Listener(
            on_press=self._on_press,
            on_release=self._on_release,
            win32_event_filter=self._win32_event_filter,
            suppress=False,
        )
        self._listener.start()
        print("[Hotkey] Listener started. Hold Ctrl+Space to record.", flush=True)

    def stop(self):
        """Stop the global keyboard listener."""
        if self._listener:
            self._listener.stop()
