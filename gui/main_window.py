"""
gui/main_window.py — Main Dashboard and Settings Window for WhisprFlow.
Features modern Windows 11 Fluent dark styling, tab navigation, takes history timeline,
and configurable real-time streaming output controls.
"""

import os
import pyperclip
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QTextEdit, QSystemTrayIcon, QMenu,
    QGraphicsDropShadowEffect, QStackedWidget, QScrollArea,
    QLineEdit, QComboBox, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QSize
from PyQt6.QtGui import QIcon, QPixmap, QColor

from gui.styles import DARK_THEME_QSS
from gui.floating_pill import FloatingPill
from gui.title_bar import CustomTitleBar
import config
import history_manager


class TakeCard(QFrame):
    """Card representing an individual speech take in the history timeline."""

    take_deleted = pyqtSignal(str)

    def __init__(self, take_data: dict, parent=None):
        super().__init__(parent)
        self.take_data = take_data
        self.setObjectName("TakeCard")
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(8)

        # ── Header Row ────────────────────────────────────────────────────────
        header = QHBoxLayout()
        header.setSpacing(8)

        # Mode Badge
        mode = self.take_data.get("mode", "smart")
        mode_badge = QLabel("🧠 SMART" if mode == "smart" else "⚡ FAST")
        mode_badge.setObjectName("BadgeSmart" if mode == "smart" else "BadgeFast")
        header.addWidget(mode_badge)

        # Streaming / Paste Badge
        is_streaming = self.take_data.get("streaming", True)
        stream_badge = QLabel("⚡ STREAMED" if is_streaming else "📋 PASTED")
        stream_badge.setObjectName("BadgeNeutral")
        header.addWidget(stream_badge)

        # Latency
        latency = self.take_data.get("latency_ms", 0)
        lat_badge = QLabel(f"{latency:.0f}ms")
        lat_badge.setObjectName("BadgeNeutral")
        header.addWidget(lat_badge)

        # Words
        wc = self.take_data.get("word_count", 0)
        words_badge = QLabel(f"{wc} words")
        words_badge.setObjectName("BadgeNeutral")
        header.addWidget(words_badge)

        header.addStretch()

        # Timestamp
        time_str = self.take_data.get("display_time", "")
        time_label = QLabel(time_str)
        time_label.setStyleSheet("color: #71717a; font-size: 11px; font-weight: 600;")
        header.addWidget(time_label)

        layout.addLayout(header)

        # ── Body Text ─────────────────────────────────────────────────────────
        text = self.take_data.get("text", "")
        text_label = QLabel(text)
        text_label.setWordWrap(True)
        text_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        text_label.setStyleSheet(
            "color: #f4f4f5; font-size: 13px; line-height: 1.5; font-weight: 400; padding: 2px 0;"
        )
        layout.addWidget(text_label)

        # ── Actions Footer ────────────────────────────────────────────────────
        actions = QHBoxLayout()
        actions.setSpacing(8)
        actions.addStretch()

        self.copy_btn = QPushButton("📋 Copy Text")
        self.copy_btn.setObjectName("SecondaryBtn")
        self.copy_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.copy_btn.clicked.connect(self._copy_text)
        actions.addWidget(self.copy_btn)

        del_btn = QPushButton("🗑️")
        del_btn.setObjectName("SecondaryBtn")
        del_btn.setToolTip("Delete this take")
        del_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        del_btn.clicked.connect(self._delete_self)
        actions.addWidget(del_btn)

        layout.addLayout(actions)

    def _copy_text(self):
        text = self.take_data.get("text", "")
        pyperclip.copy(text)
        self.copy_btn.setText("✓ Copied!")
        self.copy_btn.setStyleSheet("color: #10b981; border-color: #059669;")
        QTimer.singleShot(1500, lambda: self._reset_copy_btn())

    def _reset_copy_btn(self):
        self.copy_btn.setText("📋 Copy Text")
        self.copy_btn.setStyleSheet("")

    def _delete_self(self):
        take_id = self.take_data.get("id")
        if take_id:
            history_manager.delete_take(take_id)
            self.take_deleted.emit(take_id)


class MainWindow(QMainWindow):
    """Main application window for WhisprFlow."""

    mode_changed = pyqtSignal(bool)
    streaming_changed = pyqtSignal(bool)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Patte")
        self.resize(760, 680)
        self.setMinimumSize(680, 580)

        # Frameless window configuration
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Window)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setStyleSheet(DARK_THEME_QSS)

        # Runtime States
        self.ai_mode_enabled = config.AI_REFINEMENT_ENABLED
        self.streaming_enabled = config.STREAMING_OUTPUT_ENABLED

        # Subcomponents
        self.pill = FloatingPill()

        self._build_ui()
        self._setup_tray()
        self._load_history()
        self._update_mode_ui()
        self._update_streaming_ui()

    def _build_ui(self):
        outer_widget = QWidget(self)
        outer_widget.setObjectName("CentralWidget")
        self.setCentralWidget(outer_widget)

        outer_layout = QVBoxLayout(outer_widget)
        outer_layout.setContentsMargins(12, 12, 12, 12)

        # Container Frame
        self.container = QFrame(outer_widget)
        self.container.setObjectName("WindowContainer")

        shadow = QGraphicsDropShadowEffect(self.container)
        shadow.setBlurRadius(28)
        shadow.setColor(QColor(0, 0, 0, 190))
        shadow.setOffset(0, 8)
        self.container.setGraphicsEffect(shadow)

        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)

        # ── Custom Title Bar ──────────────────────────────────────────────────
        self.title_bar = CustomTitleBar(self)
        container_layout.addWidget(self.title_bar)

        # ── Top Navigation & Status Bar ───────────────────────────────────────
        nav_widget = QWidget(self.container)
        nav_layout = QHBoxLayout(nav_widget)
        nav_layout.setContentsMargins(20, 8, 20, 10)
        nav_layout.setSpacing(12)

        # Status Pill
        self.status_pill = QLabel("● Ready", nav_widget)
        self.status_pill.setStyleSheet(
            "background-color: #064e3b; color: #34d399; border: 1px solid #059669; "
            "border-radius: 12px; padding: 4px 12px; font-size: 11px; font-weight: 700;"
        )
        nav_layout.addWidget(self.status_pill)

        nav_layout.addStretch()

        # Tab Buttons
        self.tab_history_btn = QPushButton("🎙️  Takes & History", nav_widget)
        self.tab_history_btn.setObjectName("NavTabActive")
        self.tab_history_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.tab_history_btn.clicked.connect(lambda: self._switch_tab(0))

        self.tab_settings_btn = QPushButton("⚙️  Engine & Settings", nav_widget)
        self.tab_settings_btn.setObjectName("NavTab")
        self.tab_settings_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.tab_settings_btn.clicked.connect(lambda: self._switch_tab(1))

        nav_layout.addWidget(self.tab_history_btn)
        nav_layout.addWidget(self.tab_settings_btn)

        container_layout.addWidget(nav_widget)

        # ── Stacked Views Container ───────────────────────────────────────────
        self.views = QStackedWidget(self.container)

        self.view_history = self._build_history_view()
        self.view_settings = self._build_settings_view()

        self.views.addWidget(self.view_history)
        self.views.addWidget(self.view_settings)

        container_layout.addWidget(self.views)

        # ── Global Minimal Footer ─────────────────────────────────────────────
        footer = QWidget(self.container)
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(20, 6, 20, 12)

        self.footer_info = QLabel(
            f"STT: Whisper {config.WHISPER_MODEL.upper()}  •  Refiner: {config.LM_STUDIO_MODEL} (127.0.0.1)"
        )
        self.footer_info.setStyleSheet("color: #52525b; font-size: 11px; font-weight: 500;")

        shortcut_label = QLabel("Hotkey: Hold Ctrl+Space to speak")
        shortcut_label.setStyleSheet("color: #71717a; font-size: 11px; font-weight: 600;")

        footer_layout.addWidget(self.footer_info)
        footer_layout.addStretch()
        footer_layout.addWidget(shortcut_label)

        container_layout.addWidget(footer)
        outer_layout.addWidget(self.container)

    def _switch_tab(self, index: int):
        self.views.setCurrentIndex(index)
        if index == 0:
            self.tab_history_btn.setObjectName("NavTabActive")
            self.tab_settings_btn.setObjectName("NavTab")
        else:
            self.tab_history_btn.setObjectName("NavTab")
            self.tab_settings_btn.setObjectName("NavTabActive")
        self.tab_history_btn.style().polish(self.tab_history_btn)
        self.tab_settings_btn.style().polish(self.tab_settings_btn)

    # ──────────────────────────────────────────────────────────────────────────
    # TAB 1: TAKES & HISTORY VIEW
    # ──────────────────────────────────────────────────────────────────────────
    def _build_history_view(self) -> QWidget:
        view = QWidget()
        layout = QVBoxLayout(view)
        layout.setContentsMargins(20, 0, 20, 8)
        layout.setSpacing(12)

        # ── Hero Quick Controls Bar ───────────────────────────────────────────
        controls_card = QFrame(view)
        controls_card.setObjectName("Card")
        ctrl_layout = QHBoxLayout(controls_card)
        ctrl_layout.setContentsMargins(14, 12, 14, 12)
        ctrl_layout.setSpacing(12)

        # Mode Buttons
        mode_label = QLabel("MODE:")
        mode_label.setObjectName("MutedLabel")
        ctrl_layout.addWidget(mode_label)

        self.fast_btn = QPushButton("⚡ Fast Mode", controls_card)
        self.fast_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.fast_btn.clicked.connect(lambda: self.set_ai_mode(False))

        self.smart_btn = QPushButton("🧠 Smart Mode", controls_card)
        self.smart_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.smart_btn.clicked.connect(lambda: self.set_ai_mode(True))

        ctrl_layout.addWidget(self.fast_btn)
        ctrl_layout.addWidget(self.smart_btn)

        ctrl_layout.addStretch()

        # Quick Streaming Output Pill
        stream_label = QLabel("OUTPUT:")
        stream_label.setObjectName("MutedLabel")
        ctrl_layout.addWidget(stream_label)

        self.quick_stream_btn = QPushButton("⚡ Streaming Live", controls_card)
        self.quick_stream_btn.setObjectName("SecondaryBtn")
        self.quick_stream_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.quick_stream_btn.clicked.connect(self._toggle_streaming)
        ctrl_layout.addWidget(self.quick_stream_btn)

        layout.addWidget(controls_card)

        # ── History Header & Filter Bar ───────────────────────────────────────
        hist_header = QHBoxLayout()
        hist_header.setSpacing(10)

        self.hist_count_label = QLabel("TAKES TIMELINE")
        self.hist_count_label.setObjectName("MutedLabel")
        hist_header.addWidget(self.hist_count_label)

        hist_header.addStretch()

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Search past takes...")
        self.search_input.setFixedWidth(200)
        self.search_input.textChanged.connect(self._filter_history)
        hist_header.addWidget(self.search_input)

        self.clear_btn = QPushButton("🗑️ Clear")
        self.clear_btn.setObjectName("SecondaryBtn")
        self.clear_btn.setToolTip("Clear all takes history")
        self.clear_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.clear_btn.clicked.connect(self._clear_all_history)
        hist_header.addWidget(self.clear_btn)

        layout.addLayout(hist_header)

        # ── Scroll Area for Takes ─────────────────────────────────────────────
        self.scroll_area = QScrollArea(view)
        self.scroll_area.setWidgetResizable(True)

        self.takes_container = QWidget()
        self.takes_layout = QVBoxLayout(self.takes_container)
        self.takes_layout.setContentsMargins(0, 0, 4, 0)
        self.takes_layout.setSpacing(10)
        self.takes_layout.addStretch()

        self.scroll_area.setWidget(self.takes_container)
        layout.addWidget(self.scroll_area)

        return view

    # ──────────────────────────────────────────────────────────────────────────
    # TAB 2: ENGINE & SETTINGS VIEW
    # ──────────────────────────────────────────────────────────────────────────
    def _build_settings_view(self) -> QWidget:
        view = QWidget()
        layout = QVBoxLayout(view)
        layout.setContentsMargins(20, 0, 20, 8)
        layout.setSpacing(14)

        # ── Output Streaming Config Card ──────────────────────────────────────
        stream_card = QFrame(view)
        stream_card.setObjectName("Card")
        sc_layout = QVBoxLayout(stream_card)
        sc_layout.setContentsMargins(18, 16, 18, 16)
        sc_layout.setSpacing(10)

        sc_title = QLabel("TEXT OUTPUT INJECTION MODE")
        sc_title.setObjectName("MutedLabel")
        sc_layout.addWidget(sc_title)

        stream_toggle_layout = QHBoxLayout()
        stream_toggle_layout.setSpacing(10)

        self.cfg_stream_on = QPushButton("⚡ Real-Time Streaming (Win32 SendInput)", stream_card)
        self.cfg_stream_on.setCursor(Qt.CursorShape.PointingHandCursor)
        self.cfg_stream_on.clicked.connect(lambda: self.set_streaming_mode(True))

        self.cfg_stream_off = QPushButton("📋 Instant Paste (Ctrl+V Clipboard)", stream_card)
        self.cfg_stream_off.setCursor(Qt.CursorShape.PointingHandCursor)
        self.cfg_stream_off.clicked.connect(lambda: self.set_streaming_mode(False))

        stream_toggle_layout.addWidget(self.cfg_stream_on)
        stream_toggle_layout.addWidget(self.cfg_stream_off)
        sc_layout.addLayout(stream_toggle_layout)

        self.stream_desc = QLabel(stream_card)
        self.stream_desc.setObjectName("SubLabel")
        self.stream_desc.setWordWrap(True)
        sc_layout.addWidget(self.stream_desc)

        layout.addWidget(stream_card)

        # ── Whisper ASR Engine Card ───────────────────────────────────────────
        asr_card = QFrame(view)
        asr_card.setObjectName("Card")
        asr_layout = QVBoxLayout(asr_card)
        asr_layout.setContentsMargins(18, 16, 18, 16)
        asr_layout.setSpacing(10)

        asr_title = QLabel("LOCAL SPEECH-TO-TEXT ENGINE (CTranslate2 C++)")
        asr_title.setObjectName("MutedLabel")
        asr_layout.addWidget(asr_title)

        asr_row = QHBoxLayout()
        asr_row.setSpacing(14)

        # Model Picker
        model_vbox = QVBoxLayout()
        model_lbl = QLabel("Model Size:")
        model_lbl.setStyleSheet("color: #a1a1aa; font-size: 11px;")
        self.combo_whisper = QComboBox()
        self.combo_whisper.addItems(["tiny.en (Fastest ~400ms)", "base.en (~800ms)", "base (Multilingual)", "small"])
        self.combo_whisper.currentTextChanged.connect(self._on_whisper_model_changed)
        model_vbox.addWidget(model_lbl)
        model_vbox.addWidget(self.combo_whisper)
        asr_row.addLayout(model_vbox)

        # Language Picker
        lang_vbox = QVBoxLayout()
        lang_lbl = QLabel("Spoken Language:")
        lang_lbl.setStyleSheet("color: #a1a1aa; font-size: 11px;")
        self.combo_lang = QComboBox()
        self.combo_lang.addItems(["en (English — 2x Faster)", "auto (Auto-detect)"])
        self.combo_lang.currentTextChanged.connect(self._on_lang_changed)
        lang_vbox.addWidget(lang_lbl)
        lang_vbox.addWidget(self.combo_lang)
        asr_row.addLayout(lang_vbox)

        asr_layout.addLayout(asr_row)
        layout.addWidget(asr_card)

        # ── LM Studio / AI Engine Card ────────────────────────────────────────
        llm_card = QFrame(view)
        llm_card.setObjectName("Card")
        llm_layout = QVBoxLayout(llm_card)
        llm_layout.setContentsMargins(18, 16, 18, 16)
        llm_layout.setSpacing(10)

        llm_title = QLabel("AI TRANSCRIPT NORMALIZATION (SMART MODE)")
        llm_title.setObjectName("MutedLabel")
        llm_layout.addWidget(llm_title)

        llm_row = QHBoxLayout()
        llm_row.setSpacing(14)

        # Provider
        prov_vbox = QVBoxLayout()
        prov_lbl = QLabel("Provider:")
        prov_lbl.setStyleSheet("color: #a1a1aa; font-size: 11px;")
        self.combo_provider = QComboBox()
        self.combo_provider.addItems(["LM Studio (Local 127.0.0.1)", "Groq Cloud (Blazing Fast)", "OpenAI"])
        prov_vbox.addWidget(prov_lbl)
        prov_vbox.addWidget(self.combo_provider)
        llm_row.addLayout(prov_vbox)

        # Model Input
        m_vbox = QVBoxLayout()
        m_lbl = QLabel("Model Name:")
        m_lbl.setStyleSheet("color: #a1a1aa; font-size: 11px;")
        self.input_llm_model = QLineEdit(config.LM_STUDIO_MODEL)
        self.input_llm_model.textChanged.connect(self._on_llm_model_changed)
        m_vbox.addWidget(m_lbl)
        m_vbox.addWidget(self.input_llm_model)
        llm_row.addLayout(m_vbox)

        llm_layout.addLayout(llm_row)
        layout.addWidget(llm_card)

        layout.addStretch()
        return view

    # ──────────────────────────────────────────────────────────────────────────
    # LOGIC & EVENTS
    # ──────────────────────────────────────────────────────────────────────────
    def set_ai_mode(self, enabled: bool):
        self.ai_mode_enabled = enabled
        config.AI_REFINEMENT_ENABLED = enabled
        config.update_env_setting("AI_REFINEMENT_ENABLED", str(enabled).lower())
        self._update_mode_ui()
        self.mode_changed.emit(enabled)

    def _update_mode_ui(self):
        if self.ai_mode_enabled:
            self.smart_btn.setObjectName("ModeActiveSmart")
            self.fast_btn.setObjectName("ModeInactive")
            self.status_pill.setText("● Smart Mode Ready")
            self.status_pill.setStyleSheet(
                "background-color: #2e1065; color: #c4b5fd; border: 1px solid #7c3aed; "
                "border-radius: 12px; padding: 4px 12px; font-size: 11px; font-weight: 700;"
            )
        else:
            self.smart_btn.setObjectName("ModeInactive")
            self.fast_btn.setObjectName("ModeActiveFast")
            self.status_pill.setText("● Fast Mode Ready")
            self.status_pill.setStyleSheet(
                "background-color: #0c4a6e; color: #7dd3fc; border: 1px solid #0284c7; "
                "border-radius: 12px; padding: 4px 12px; font-size: 11px; font-weight: 700;"
            )
        self.smart_btn.style().polish(self.smart_btn)
        self.fast_btn.style().polish(self.fast_btn)

    def _toggle_streaming(self):
        self.set_streaming_mode(not self.streaming_enabled)

    def set_streaming_mode(self, enabled: bool):
        self.streaming_enabled = enabled
        config.STREAMING_OUTPUT_ENABLED = enabled
        config.update_env_setting("STREAMING_OUTPUT_ENABLED", str(enabled).lower())
        self._update_streaming_ui()
        self.streaming_changed.emit(enabled)

    def _update_streaming_ui(self):
        if self.streaming_enabled:
            self.quick_stream_btn.setText("⚡ Streaming: Live Keystrokes")
            self.quick_stream_btn.setStyleSheet("color: #818cf8; border-color: #4f46e5;")
            self.cfg_stream_on.setObjectName("ModeActiveSmart")
            self.cfg_stream_off.setObjectName("ModeInactive")
            self.stream_desc.setText(
                "Live Keystrokes: Words are typed directly into the active cursor window character-by-character "
                "as they stream from S1-Mini (~350ms TTFT). Does not overwrite your clipboard."
            )
        else:
            self.quick_stream_btn.setText("📋 Output: Clipboard Paste")
            self.quick_stream_btn.setStyleSheet("color: #38bdf8; border-color: #0284c7;")
            self.cfg_stream_on.setObjectName("ModeInactive")
            self.cfg_stream_off.setObjectName("ModeActiveFast")
            self.stream_desc.setText(
                "Clipboard Paste: Waits for the full refined sentence to complete, then injects it "
                "all at once via Ctrl+V and automatically restores your original clipboard."
            )
        self.cfg_stream_on.style().polish(self.cfg_stream_on)
        self.cfg_stream_off.style().polish(self.cfg_stream_off)

    def _on_whisper_model_changed(self, text: str):
        val = text.split()[0].strip()
        config.WHISPER_MODEL = val
        config.update_env_setting("WHISPER_MODEL", val)

    def _on_lang_changed(self, text: str):
        val = text.split()[0].strip()
        config.WHISPER_LANGUAGE = val
        config.update_env_setting("WHISPER_LANGUAGE", val)

    def _on_llm_model_changed(self, text: str):
        val = text.strip()
        if val:
            config.LM_STUDIO_MODEL = val
            config.update_env_setting("LM_STUDIO_MODEL", val)

    # ──────────────────────────────────────────────────────────────────────────
    # TAKES TIMELINE MANAGEMENT
    # ──────────────────────────────────────────────────────────────────────────
    def _load_history(self):
        # Clear existing card widgets
        while self.takes_layout.count() > 1:
            item = self.takes_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        takes = history_manager.get_takes()
        count = len(takes)
        self.hist_count_label.setText(f"TAKES TIMELINE ({count})")

        if not takes:
            empty_card = QFrame()
            empty_card.setObjectName("TakeCard")
            e_layout = QVBoxLayout(empty_card)
            e_layout.setContentsMargins(20, 24, 20, 24)
            lbl1 = QLabel("🎙️  No speech takes yet")
            lbl1.setStyleSheet("color: #ffffff; font-size: 14px; font-weight: 700;")
            lbl2 = QLabel("Press and hold Ctrl+Space anywhere to dictate. Your takes will be archived here automatically.")
            lbl2.setStyleSheet("color: #71717a; font-size: 12px;")
            e_layout.addWidget(lbl1)
            e_layout.addWidget(lbl2)
            self.takes_layout.insertWidget(0, empty_card)
            return

        for take in takes:
            card = TakeCard(take)
            card.take_deleted.connect(lambda _: self._load_history())
            self.takes_layout.insertWidget(self.takes_layout.count() - 1, card)

    def add_new_take(self, text: str, raw_text: str, latency_ms: float):
        """Append a newly completed dictation take with zero UI thread lag."""
        mode = "smart" if self.ai_mode_enabled else "fast"
        entry = history_manager.add_take(
            text=text,
            raw_text=raw_text,
            mode=mode,
            latency_ms=latency_ms,
            streaming=self.streaming_enabled,
        )
        if entry and self.isVisible():
            card = TakeCard(entry)
            card.take_deleted.connect(lambda _: self._load_history())
            self.takes_layout.insertWidget(0, card)
            count = len(history_manager.get_takes())
            self.hist_count_label.setText(f"TAKES TIMELINE ({count})")

    def _filter_history(self, query: str):
        q = query.strip().lower()
        for i in range(self.takes_layout.count() - 1):
            item = self.takes_layout.itemAt(i)
            if item and item.widget() and isinstance(item.widget(), TakeCard):
                card = item.widget()
                text = card.take_data.get("text", "").lower()
                card.setVisible(q in text if q else True)

    def _clear_all_history(self):
        reply = QMessageBox.question(
            self,
            "Clear History",
            "Are you sure you want to delete all stored dictation takes?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            history_manager.clear_history()
            self._load_history()

    # ──────────────────────────────────────────────────────────────────────────
    # STATUS & FLOATING PILL SIGNALS
    # ──────────────────────────────────────────────────────────────────────────
    def set_status_recording(self):
        self.status_pill.setText("● Listening...")
        self.status_pill.setStyleSheet(
            "background-color: #450a0a; color: #f87171; border: 1px solid #ef4444; "
            "border-radius: 12px; padding: 4px 12px; font-size: 11px; font-weight: 700;"
        )
        self.tray_icon.setIcon(self.icon_rec)
        self.pill.show_recording()

    def set_status_transcribing(self):
        self.status_pill.setText("⚡ Transcribing...")
        self.status_pill.setStyleSheet(
            "background-color: #0c4a6e; color: #38bdf8; border: 1px solid #0284c7; "
            "border-radius: 12px; padding: 4px 12px; font-size: 11px; font-weight: 700;"
        )
        self.tray_icon.setIcon(self.icon_proc)
        self.pill.show_transcribing()

    def set_status_refining(self):
        self.status_pill.setText("🧠 AI Polishing...")
        self.status_pill.setStyleSheet(
            "background-color: #2e1065; color: #c084fc; border: 1px solid #9333ea; "
            "border-radius: 12px; padding: 4px 12px; font-size: 11px; font-weight: 700;"
        )
        self.tray_icon.setIcon(self.icon_proc)
        self.pill.show_refining()

    def set_status_pasted(self, text: str):
        self._update_mode_ui()
        self.tray_icon.setIcon(self.icon_idle)
        # Instantly dismiss the micro-pill — zero screen clutter or lingering popups
        self.pill.dismiss()

    def set_status_idle_with_msg(self, msg: str):
        self.status_pill.setText(f"● {msg}")
        self.status_pill.setStyleSheet(
            "background-color: #1e1e24; color: #a1a1aa; border: 1px solid #2e2e38; "
            "border-radius: 12px; padding: 4px 12px; font-size: 11px; font-weight: 700;"
        )
        self.tray_icon.setIcon(self.icon_idle)
        self.pill.show_error(msg)
        QTimer.singleShot(2500, self._update_mode_ui)

    def _setup_tray(self):
        self.tray_icon = QSystemTrayIcon(self)
        self.icon_idle = QIcon("assets/tray_idle.png")
        self.icon_rec = QIcon("assets/tray_recording.png")
        self.icon_proc = QIcon("assets/tray_processing.png")

        self.tray_icon.setIcon(self.icon_idle)
        self.tray_icon.setToolTip("Patte — Voice Dictation (Ctrl+Space)")

        tray_menu = QMenu()
        tray_menu.setStyleSheet("""
            QMenu {
                background-color: #16161d;
                color: #f4f4f5;
                border: 1px solid #282834;
                padding: 6px;
                border-radius: 8px;
            }
            QMenu::item {
                padding: 6px 20px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: #4f46e5;
                color: #ffffff;
            }
        """)

        show_action = tray_menu.addAction("Open Dashboard")
        show_action.triggered.connect(self.show_normal)
        tray_menu.addSeparator()

        fast_action = tray_menu.addAction("⚡ Fast Mode")
        fast_action.triggered.connect(lambda: self.set_ai_mode(False))

        smart_action = tray_menu.addAction("🧠 Smart Mode")
        smart_action.triggered.connect(lambda: self.set_ai_mode(True))
        tray_menu.addSeparator()

        quit_action = tray_menu.addAction("Quit Patte")
        quit_action.triggered.connect(self.close)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self._on_tray_activated)
        self.tray_icon.show()

    def _on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            if self.isVisible():
                self.hide()
            else:
                self.show_normal()

    def show_normal(self):
        self.show()
        self.raise_()
        self.activateWindow()
