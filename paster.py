"""
paster.py — Native Windows text output (live token streaming via Win32 SendInput
and instant clipboard paste).
Uses explicit 64-bit ctypes signatures and chunked SendInput batching to prevent
Windows input queue overflow on long text.
"""

import time
import threading
import ctypes
from ctypes import wintypes
import pyperclip
from pynput.keyboard import Controller, Key

_keyboard = Controller()
_user32 = ctypes.windll.user32

# Win32 Constants
INPUT_KEYBOARD = 1
KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_UNICODE = 0x0004
VK_CONTROL = 0x11
VK_SHIFT = 0x10
VK_MENU = 0x12
VK_RETURN = 0x0D
VK_V = 0x56

ULONG_PTR = ctypes.c_uint64 if ctypes.sizeof(ctypes.c_void_p) == 8 else ctypes.c_uint32


class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", wintypes.LONG),
        ("dy", wintypes.LONG),
        ("mouseData", wintypes.DWORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ULONG_PTR),
    ]


class KEYBDINPUT(ctypes.Structure):
    _fields_ = [
        ("wVk", wintypes.WORD),
        ("wScan", wintypes.WORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ULONG_PTR),
    ]


class HARDWAREINPUT(ctypes.Structure):
    _fields_ = [
        ("uMsg", wintypes.DWORD),
        ("wParamL", wintypes.WORD),
        ("wParamH", wintypes.WORD),
    ]


class _INPUTunion(ctypes.Union):
    _fields_ = [
        ("mi", MOUSEINPUT),
        ("ki", KEYBDINPUT),
        ("hi", HARDWAREINPUT),
    ]


class INPUT(ctypes.Structure):
    _fields_ = [
        ("type", wintypes.DWORD),
        ("union", _INPUTunion),
    ]


# Explicit 64-bit Win32 function prototypes
_user32.SendInput.argtypes = [wintypes.UINT, ctypes.POINTER(INPUT), ctypes.c_int]
_user32.SendInput.restype = wintypes.UINT

_user32.keybd_event.argtypes = [wintypes.BYTE, wintypes.BYTE, wintypes.DWORD, ULONG_PTR]
_user32.keybd_event.restype = None


def release_modifiers():
    """Ensure Ctrl, Shift, and Alt are released before injecting input."""
    try:
        _user32.keybd_event(VK_CONTROL, 0, KEYEVENTF_KEYUP, 0)
        _user32.keybd_event(VK_SHIFT, 0, KEYEVENTF_KEYUP, 0)
        _user32.keybd_event(VK_MENU, 0, KEYEVENTF_KEYUP, 0)
    except Exception:
        pass
    for key in (Key.ctrl, Key.ctrl_l, Key.ctrl_r, Key.shift, Key.alt):
        try:
            _keyboard.release(key)
        except Exception:
            pass


def prepare_for_typing():
    """Release held hotkey modifiers immediately (zero blocking sleep)."""
    release_modifiers()


def type_token(token: str):
    """
    Immediately inject a streamed text token into the active window using
    native Win32 SendInput (KEYEVENTF_UNICODE). Batches in small chunks so
    long texts never overflow the Windows input queue.
    """
    if not token:
        return

    inputs = []
    normalized = token.replace("\r\n", "\n")

    for ch in normalized:
        if ch == "\n":
            down = INPUT(type=INPUT_KEYBOARD)
            down.union.ki = KEYBDINPUT(wVk=VK_RETURN, wScan=0, dwFlags=0, time=0, dwExtraInfo=0)
            up = INPUT(type=INPUT_KEYBOARD)
            up.union.ki = KEYBDINPUT(wVk=VK_RETURN, wScan=0, dwFlags=KEYEVENTF_KEYUP, time=0, dwExtraInfo=0)
            inputs.append(down)
            inputs.append(up)
        else:
            utf16_bytes = ch.encode("utf-16-le")
            for i in range(0, len(utf16_bytes), 2):
                code_unit = int.from_bytes(utf16_bytes[i:i + 2], "little")
                down = INPUT(type=INPUT_KEYBOARD)
                down.union.ki = KEYBDINPUT(
                    wVk=0, wScan=code_unit, dwFlags=KEYEVENTF_UNICODE, time=0, dwExtraInfo=0
                )
                up = INPUT(type=INPUT_KEYBOARD)
                up.union.ki = KEYBDINPUT(
                    wVk=0,
                    wScan=code_unit,
                    dwFlags=KEYEVENTF_UNICODE | KEYEVENTF_KEYUP,
                    time=0,
                    dwExtraInfo=0,
                )
                inputs.append(down)
                inputs.append(up)

    # Send in safe batches of up to 32 INPUT structs (16 characters) at a time
    batch_size = 32
    for start in range(0, len(inputs), batch_size):
        batch = inputs[start:start + batch_size]
        array_type = INPUT * len(batch)
        input_array = array_type(*batch)
        _user32.SendInput(len(batch), input_array, ctypes.sizeof(INPUT))
        if start + batch_size < len(inputs):
            time.sleep(0.002)


def _send_ctrl_v():
    """Simulate Ctrl+V using native Windows user32 keybd_event."""
    try:
        _user32.keybd_event(VK_V, 0, KEYEVENTF_KEYUP, 0)
        _user32.keybd_event(VK_CONTROL, 0, KEYEVENTF_KEYUP, 0)
        time.sleep(0.02)
        _user32.keybd_event(VK_CONTROL, 0, 0, 0)
        _user32.keybd_event(VK_V, 0, 0, 0)
        time.sleep(0.04)
        _user32.keybd_event(VK_V, 0, KEYEVENTF_KEYUP, 0)
        _user32.keybd_event(VK_CONTROL, 0, KEYEVENTF_KEYUP, 0)
    except Exception:
        _keyboard.press(Key.ctrl_l)
        _keyboard.press("v")
        time.sleep(0.04)
        _keyboard.release("v")
        _keyboard.release(Key.ctrl_l)


def paste_text(text: str):
    """
    Paste text at the current cursor position via clipboard.
    Saves and restores original clipboard contents after pasting.
    """
    try:
        try:
            original_clipboard = pyperclip.paste()
        except Exception:
            original_clipboard = ""

        pyperclip.copy(text)

        time.sleep(0.10)
        release_modifiers()
        time.sleep(0.02)

        _send_ctrl_v()

        print(f"[Paster] [OK] Pasted {len(text)} characters: {text[:80]}{'...' if len(text) > 80 else ''}", flush=True)

        def restore():
            time.sleep(0.8)
            try:
                pyperclip.copy(original_clipboard)
            except Exception:
                pass

        threading.Thread(target=restore, daemon=True).start()

    except Exception as e:
        print(f"[Paster] Error pasting text: {e}", flush=True)
