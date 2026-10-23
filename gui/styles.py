"""
gui/styles.py — Modern Windows 11 Fluent Dark Theme QSS stylesheet.
Designed for a high-end, obsidian-dark desktop voice AI application.
"""

DARK_THEME_QSS = """
/* Global Reset & Base */
QWidget {
    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, 'Roboto', sans-serif;
    color: #f4f4f5;
    outline: none;
}

/* Window Outer Container */
QWidget#WindowContainer {
    background-color: #0f0f13;
    border: 1px solid #282834;
    border-radius: 14px;
}

QWidget#CentralWidget {
    background-color: transparent;
}

/* Labels */
QLabel {
    color: #f4f4f5;
}

QLabel#MutedLabel {
    color: #71717a;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 1.2px;
    text-transform: uppercase;
}

QLabel#SubLabel {
    color: #a1a1aa;
    font-size: 12px;
    line-height: 1.4;
}

/* Cards & Surface Containers */
QFrame#Card {
    background-color: #16161d;
    border: 1px solid #262633;
    border-radius: 12px;
}

QFrame#CardElevated {
    background-color: #1b1b24;
    border: 1px solid #2f2f3f;
    border-radius: 12px;
}

QFrame#InnerCard {
    background-color: #131318;
    border: 1px solid #242430;
    border-radius: 8px;
}

/* Nav Tab Buttons */
QPushButton#NavTab {
    background-color: transparent;
    color: #9ca3af;
    border: none;
    border-radius: 8px;
    padding: 8px 16px;
    font-size: 13px;
    font-weight: 600;
    text-align: center;
}

QPushButton#NavTab:hover {
    background-color: #1f1f2a;
    color: #f4f4f5;
}

QPushButton#NavTabActive {
    background-color: #272736;
    color: #ffffff;
    border: 1px solid #3b3b4f;
    border-radius: 8px;
    padding: 8px 16px;
    font-size: 13px;
    font-weight: 700;
    text-align: center;
}

/* Primary Action Buttons */
QPushButton#PrimaryBtn {
    background-color: #6366f1;
    color: #ffffff;
    border: 1px solid #818cf8;
    border-radius: 8px;
    padding: 9px 18px;
    font-size: 13px;
    font-weight: 700;
}

QPushButton#PrimaryBtn:hover {
    background-color: #4f46e5;
}

QPushButton#PrimaryBtn:pressed {
    background-color: #4338ca;
}

/* Secondary & Action Buttons */
QPushButton#SecondaryBtn {
    background-color: #22222d;
    color: #e4e4e7;
    border: 1px solid #323242;
    border-radius: 8px;
    padding: 7px 14px;
    font-size: 12px;
    font-weight: 600;
}

QPushButton#SecondaryBtn:hover {
    background-color: #2d2d3c;
    border-color: #434358;
    color: #ffffff;
}

QPushButton#SecondaryBtn:pressed {
    background-color: #1a1a23;
}

/* Mode Switcher Segmented Buttons */
QPushButton#ModeActiveSmart {
    background-color: #7c3aed;
    color: #ffffff;
    border: 1px solid #a78bfa;
    border-radius: 8px;
    font-weight: 700;
    padding: 10px 18px;
    font-size: 13px;
}

QPushButton#ModeActiveFast {
    background-color: #0284c7;
    color: #ffffff;
    border: 1px solid #38bdf8;
    border-radius: 8px;
    font-weight: 700;
    padding: 10px 18px;
    font-size: 13px;
}

QPushButton#ModeInactive {
    background-color: #171720;
    color: #9ca3af;
    border: 1px solid #272736;
    border-radius: 8px;
    font-weight: 500;
    padding: 10px 18px;
    font-size: 13px;
}

QPushButton#ModeInactive:hover {
    background-color: #20202c;
    color: #f4f4f5;
    border-color: #38384a;
}

/* Search Input & Line Edits */
QLineEdit {
    background-color: #131319;
    color: #f4f4f5;
    border: 1px solid #272736;
    border-radius: 8px;
    padding: 8px 12px;
    font-size: 12px;
    selection-background-color: #6366f1;
}

QLineEdit:focus {
    border: 1px solid #6366f1;
    background-color: #161620;
}

/* Comboboxes */
QComboBox {
    background-color: #14141b;
    color: #f4f4f5;
    border: 1px solid #2a2a38;
    border-radius: 8px;
    padding: 7px 12px;
    font-size: 12px;
    font-weight: 600;
}

QComboBox:hover {
    border-color: #3f3f54;
    background-color: #1b1b24;
}

QComboBox::drop-down {
    border: none;
    width: 24px;
}

QComboBox QAbstractItemView {
    background-color: #1a1a24;
    color: #f4f4f5;
    border: 1px solid #2f2f40;
    selection-background-color: #4f46e5;
    border-radius: 6px;
    padding: 4px;
}

/* Scroll Areas & Scrollbars */
QScrollArea {
    background-color: transparent;
    border: none;
}

QScrollBar:vertical {
    border: none;
    background: transparent;
    width: 6px;
    margin: 4px 0 4px 0;
}

QScrollBar::handle:vertical {
    background: #343444;
    min-height: 24px;
    border-radius: 3px;
}

QScrollBar::handle:vertical:hover {
    background: #4a4a60;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

/* Take History Card */
QFrame#TakeCard {
    background-color: #15151c;
    border: 1px solid #232330;
    border-radius: 10px;
}

QFrame#TakeCard:hover {
    background-color: #191922;
    border-color: #353547;
}

/* Badges */
QLabel#BadgeSmart {
    background-color: #2e1065;
    color: #c4b5fd;
    border: 1px solid #6d28d9;
    border-radius: 6px;
    padding: 2px 8px;
    font-size: 10px;
    font-weight: 700;
}

QLabel#BadgeFast {
    background-color: #082f49;
    color: #7dd3fc;
    border: 1px solid #0369a1;
    border-radius: 6px;
    padding: 2px 8px;
    font-size: 10px;
    font-weight: 700;
}

QLabel#BadgeNeutral {
    background-color: #1e1e27;
    color: #a1a1aa;
    border: 1px solid #30303e;
    border-radius: 6px;
    padding: 2px 8px;
    font-size: 10px;
    font-weight: 600;
}
"""

FLOATING_PILL_QSS = """
QFrame#PillFrame {
    background-color: rgba(18, 18, 24, 0.94);
    border: 1.5px solid #6366f1;
    border-radius: 20px;
}
"""
