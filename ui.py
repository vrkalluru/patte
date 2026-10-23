"""
ui.py — Floating status window + system tray for WhisprFlow.
Uses tkinter (built into Python) for a reliable always-visible status indicator.
Falls back gracefully if tray icon fails.
"""

import threading
import tkinter as tk
from tkinter import font as tkfont
import pystray
from PIL import Image, ImageDraw

# State colors
COLOR_IDLE       = "#22c55e"   # Green
COLOR_RECORDING  = "#ef4444"   # Red
COLOR_PROCESSING = "#eab308"   # Yellow

STATE_LABELS = {
    "idle":       ("[idle]  Hold Ctrl+Space to record", COLOR_IDLE),
    "recording":  ("[REC]   Recording...",              COLOR_RECORDING),
    "processing": ("[...]   Processing...",             COLOR_PROCESSING),
}


def _make_tray_image(color_hex: str, size: int = 64) -> Image.Image:
    r = int(color_hex[1:3], 16)
    g = int(color_hex[3:5], 16)
    b = int(color_hex[5:7], 16)
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    margin = 4
    draw.ellipse([margin, margin, size - margin, size - margin],
                 fill=(r, g, b, 255), outline=(255, 255, 255, 180), width=2)
    return img


class TrayUI:
    """
    Small floating status window + optional system tray icon.
    The floating window is the primary UI — always visible, draggable.
    """

    def __init__(self, on_quit_callback):
        self._on_quit = on_quit_callback
        self._state = "idle"
        self._root: tk.Tk | None = None
        self._label: tk.Label | None = None
        self._tray_icon: pystray.Icon | None = None

    # ── Public state methods ────────────────────────────────────────────────

    def set_idle(self):
        self._state = "idle"
        self._update_window()
        self._update_tray()

    def set_recording(self):
        self._state = "recording"
        self._update_window()
        self._update_tray()

    def set_processing(self):
        self._state = "processing"
        self._update_window()
        self._update_tray()

    def notify(self, title: str, message: str):
        print(f"[UI] {title}: {message}")
        # Flash the window border briefly as a notification
        if self._root:
            try:
                self._root.after(0, lambda: self._flash_notify(message))
            except Exception:
                pass

    # ── Window updates (must run on main thread via after()) ───────────────

    def _update_window(self):
        if self._root and self._label:
            text, color = STATE_LABELS[self._state]
            self._root.after(0, lambda: self._apply_state(text, color))

    def _apply_state(self, text: str, color: str):
        try:
            self._label.config(text=text, fg=color)
            self._root.update_idletasks()
        except Exception:
            pass

    def _flash_notify(self, message: str):
        try:
            orig = self._root.cget("bg")
            self._root.config(bg="#3b82f6")
            self._root.after(400, lambda: self._root.config(bg=orig))
        except Exception:
            pass

    # ── Tray icon ──────────────────────────────────────────────────────────

    def _start_tray(self):
        try:
            img = _make_tray_image(COLOR_IDLE)
            menu = pystray.Menu(
                pystray.MenuItem("WhisprFlow", None, enabled=False),
                pystray.MenuItem("Show window", self._show_window),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem("Quit", self._quit_from_tray),
            )
            self._tray_icon = pystray.Icon("WhisprFlow", img, "WhisprFlow", menu)
            self._tray_icon.run()
        except Exception as e:
            print(f"[UI] Tray icon failed (non-fatal): {e}")

    def _update_tray(self):
        if self._tray_icon:
            try:
                color = STATE_LABELS[self._state][1]
                self._tray_icon.icon = _make_tray_image(color)
                self._tray_icon.title = f"WhisprFlow — {self._state.capitalize()}"
            except Exception:
                pass

    def _show_window(self, icon=None, item=None):
        if self._root:
            self._root.after(0, self._root.deiconify)

    def _quit_from_tray(self, icon=None, item=None):
        if self._tray_icon:
            self._tray_icon.stop()
        if self._root:
            self._root.after(0, self._do_quit)

    def _do_quit(self):
        try:
            self._root.destroy()
        except Exception:
            pass
        self._on_quit()

    # ── Main loop (call from main thread) ──────────────────────────────────

    def start(self):
        """Build and run the tkinter window (blocking). Call from main thread."""
        self._root = tk.Tk()
        root = self._root

        root.title("WhisprFlow")
        root.resizable(False, False)
        root.attributes("-topmost", True)        # Always on top
        root.attributes("-alpha", 0.95)          # Slight transparency
        root.configure(bg="#1e1e2e")

        # Position top-right corner of primary screen (fixed coords, no overrideredirect)
        root.geometry("280x50+1220+20")

        # Make window draggable
        root.bind("<ButtonPress-1>",   self._drag_start)
        root.bind("<B1-Motion>",       self._drag_motion)

        # Status label
        f = tkfont.Font(family="Segoe UI", size=11, weight="bold")
        self._label = tk.Label(
            root,
            text="[idle]  Hold Ctrl+Space",
            fg=COLOR_IDLE,
            bg="#1e1e2e",
            font=f,
            padx=12,
            pady=10,
            cursor="hand2",
        )
        self._label.pack(fill=tk.BOTH, expand=True)

        # Right-click menu
        ctx_menu = tk.Menu(root, tearoff=0)
        ctx_menu.add_command(label="Quit WhisprFlow", command=self._do_quit)
        root.bind("<Button-3>", lambda e: ctx_menu.tk_popup(e.x_root, e.y_root))
        self._label.bind("<Button-3>", lambda e: ctx_menu.tk_popup(e.x_root, e.y_root))

        # Start tray icon in background thread
        threading.Thread(target=self._start_tray, daemon=True).start()

        root.protocol("WM_DELETE_WINDOW", self._do_quit)
        root.mainloop()

    # ── Drag support ───────────────────────────────────────────────────────

    def _drag_start(self, event):
        self._drag_x = event.x
        self._drag_y = event.y

    def _drag_motion(self, event):
        if self._root:
            x = self._root.winfo_x() + (event.x - self._drag_x)
            y = self._root.winfo_y() + (event.y - self._drag_y)
            self._root.geometry(f"+{x}+{y}")
