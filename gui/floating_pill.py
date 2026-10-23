"""
gui/floating_pill.py — Ultra-minimal, unobtrusive voice dictation micro-pill.
Designed like Wispr Flow / Superwhisper: featherweight, compact, never steals focus,
and instantly vanishes the millisecond dictation completes.
"""

from PyQt6.QtWidgets import QWidget, QFrame, QHBoxLayout, QLabel, QGraphicsDropShadowEffect
from PyQt6.QtCore import Qt, QTimer, QPoint
from PyQt6.QtGui import QColor


class FloatingPill(QWidget):
    """
    Featherweight floating micro-indicator displayed during speech dictation.
    Never accepts focus, never steals cursor position, and vanishes immediately when done.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        # Borderless, floating, always-on-top, non-activating tool window
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool |
            Qt.WindowType.WindowDoesNotAcceptFocus
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)

        self._build_ui()

    def _build_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)

        self.pill_frame = QFrame(self)
        self.pill_frame.setObjectName("MicroPillFrame")
        self.pill_frame.setFixedHeight(28)

        # Ambient soft shadow
        shadow = QGraphicsDropShadowEffect(self.pill_frame)
        shadow.setBlurRadius(16)
        shadow.setColor(QColor(0, 0, 0, 140))
        shadow.setOffset(0, 3)
        self.pill_frame.setGraphicsEffect(shadow)

        frame_layout = QHBoxLayout(self.pill_frame)
        frame_layout.setContentsMargins(10, 0, 12, 0)
        frame_layout.setSpacing(6)

        # Micro Indicator Dot
        self.dot_label = QLabel("●", self.pill_frame)
        self.dot_label.setStyleSheet("color: #f43f5e; font-size: 10px;")

        # Micro Status Text
        self.text_label = QLabel("Listening", self.pill_frame)
        self.text_label.setStyleSheet(
            "color: #e4e4e7; font-family: 'Segoe UI', -apple-system, sans-serif; "
            "font-size: 11px; font-weight: 600; letter-spacing: 0.3px;"
        )

        frame_layout.addWidget(self.dot_label)
        frame_layout.addWidget(self.text_label)

        layout.addWidget(self.pill_frame)
        self._apply_style("#f43f5e")

    def _apply_style(self, accent_color: str):
        self.pill_frame.setStyleSheet(f"""
            QFrame#MicroPillFrame {{
                background-color: rgba(14, 14, 18, 0.92);
                border: 1px solid rgba(255, 255, 255, 0.12);
                border-radius: 14px;
            }}
        """)
        self.dot_label.setStyleSheet(f"color: {accent_color}; font-size: 10px;")

    def _position_bottom_center(self):
        """Positions the pill unobtrusively near the bottom center of the screen."""
        screen = self.screen()
        if not screen:
            from PyQt6.QtWidgets import QApplication
            screen = QApplication.primaryScreen()

        geo = screen.geometry()
        self.adjustSize()
        x = geo.x() + (geo.width() - self.width()) // 2
        y = geo.y() + geo.height() - self.height() - 65
        self.move(QPoint(x, y))

    def show_recording(self):
        """Show minimal recording indicator."""
        self._apply_style("#f43f5e")  # Soft Coral Red
        self.text_label.setText("Listening")
        self._position_bottom_center()
        self.show()

    def show_transcribing(self):
        """Show fast transcribing indicator."""
        self._apply_style("#38bdf8")  # Cyan
        self.text_label.setText("Processing")
        self._position_bottom_center()
        self.show()

    def show_refining(self):
        """Show AI refining indicator."""
        self._apply_style("#a855f7")  # Violet
        self.text_label.setText("Polishing")
        self._position_bottom_center()
        self.show()

    def dismiss(self):
        """Immediately hide the pill with zero lingering screen clutter."""
        self.hide()

    def show_error(self, msg: str):
        """Briefly show small hint only if speech was not detected, then hide in 1.2s."""
        self._apply_style("#eab308")
        self.text_label.setText(msg)
        self._position_bottom_center()
        self.show()
        QTimer.singleShot(1200, self.hide)
