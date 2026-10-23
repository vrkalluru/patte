"""
gui/title_bar.py — Modern custom title bar for WhisprFlow.
Features fluid window dragging, title with version badge, and minimal window controls.
"""

from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QPixmap


class CustomTitleBar(QWidget):
    """Modern custom window title bar replacing standard Windows title bar."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self._drag_pos = QPoint()

        self.setFixedHeight(44)
        self.setStyleSheet("""
            QWidget {
                background-color: #0f0f13;
                border-top-left-radius: 14px;
                border-top-right-radius: 14px;
            }
            QLabel#TitleText {
                color: #ffffff;
                font-family: 'Segoe UI', sans-serif;
                font-size: 13px;
                font-weight: 700;
                letter-spacing: 0.3px;
            }
            QLabel#VersionBadge {
                background-color: #1e1e28;
                color: #818cf8;
                border: 1px solid #37374a;
                border-radius: 5px;
                padding: 2px 7px;
                font-size: 10px;
                font-weight: 700;
                letter-spacing: 0.5px;
            }
            QPushButton#TitleBtn {
                background-color: transparent;
                color: #9ca3af;
                border: none;
                border-radius: 6px;
                font-size: 13px;
                font-weight: bold;
                padding: 0px;
                width: 32px;
                height: 28px;
            }
            QPushButton#TitleBtn:hover {
                background-color: #262633;
                color: #ffffff;
            }
            QPushButton#CloseBtn {
                background-color: transparent;
                color: #9ca3af;
                border: none;
                border-radius: 6px;
                font-size: 13px;
                font-weight: bold;
                padding: 0px;
                width: 32px;
                height: 28px;
            }
            QPushButton#CloseBtn:hover {
                background-color: #e11d48;
                color: #ffffff;
            }
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 0, 12, 0)
        layout.setSpacing(10)

        # App Icon
        icon_label = QLabel(self)
        pix = QPixmap("assets/tray_idle.png").scaled(
            20, 20, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
        )
        icon_label.setPixmap(pix)
        layout.addWidget(icon_label)

        # Title
        title_label = QLabel("Patte", self)
        title_label.setObjectName("TitleText")
        layout.addWidget(title_label)

        # Tag
        badge = QLabel("PRO v2.0", self)
        badge.setObjectName("VersionBadge")
        layout.addWidget(badge)

        layout.addStretch()

        # Window Controls
        self.min_btn = QPushButton("─", self)
        self.min_btn.setObjectName("TitleBtn")
        self.min_btn.setToolTip("Minimize to Tray")
        self.min_btn.clicked.connect(self._on_minimize)

        self.close_btn = QPushButton("✕", self)
        self.close_btn.setObjectName("CloseBtn")
        self.close_btn.setToolTip("Minimize to System Tray")
        self.close_btn.clicked.connect(self._on_close)

        layout.addWidget(self.min_btn)
        layout.addWidget(self.close_btn)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.parent_window.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and not self._drag_pos.isNull():
            self.parent_window.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()

    def _on_minimize(self):
        if self.parent_window:
            self.parent_window.showMinimized()

    def _on_close(self):
        if self.parent_window:
            self.parent_window.hide()
