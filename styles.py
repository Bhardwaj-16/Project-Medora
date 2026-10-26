# styles.py - All QSS stylesheets for Project MEDORA (Windows XP style)
# Authentic XP Luna theme: silver/olive chrome, deep blue titlebar,
# raised/sunken borders, Tahoma font, high-contrast tooltips and tables.

XP_STYLE = """
QMainWindow {
    background-color: #ECE9D8;
}
QWidget {
    background-color: #ECE9D8;
    font-family: Tahoma, "Microsoft Sans Serif", "MS Sans Serif", Arial;
    font-size: 9pt;
    color: #000000;
}

/* ── Tooltips (High-Contrast Classic Windows XP Yellow Box) ── */
QToolTip {
    background-color: #FFFFE1;
    color: #000000;
    border: 1px solid #000000;
    font-family: Tahoma, "Microsoft Sans Serif", Arial;
    font-size: 8.5pt;
    padding: 3px 6px;
}

/* ── Menu Bar ─────────────────────────────────────────────── */
QMenuBar {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #0A246A, stop:0.4 #184CA0, stop:1 #0050A0);
    color: white;
    font-family: Tahoma, "MS Sans Serif", Arial;
    font-size: 9pt;
    spacing: 1px;
    padding: 2px 1px;
    border-bottom: 1px solid #002277;
}
QMenuBar::item {
    background: transparent;
    padding: 3px 9px;
    color: #FFFFFF;
}
QMenuBar::item:selected {
    background: #316AC5;
    color: #FFFFFF;
}
QMenuBar::item:pressed {
    background: #183C80;
    color: #FFFFFF;
}
QMenu {
    background-color: #FFFFFF;
    border: 1px solid #716F64;
    font-family: Tahoma, Arial;
    font-size: 9pt;
    color: #000000;
    padding: 2px;
}
QMenu::item {
    padding: 4px 24px 4px 20px;
    color: #000000;
}
QMenu::item:selected {
    background-color: #316AC5;
    color: #FFFFFF;
}
QMenu::separator {
    height: 1px;
    background: #ACA899;
    margin: 2px 4px;
}

/* ── Windows XP Toolbar ───────────────────────────────────── */
QToolBar {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #F6F4ED, stop:0.5 #EBE7DA, stop:1 #D9D4C7);
    border-top: 1px solid #FFFFFF;
    border-bottom: 1px solid #999587;
    spacing: 3px;
    padding: 2px 4px;
}
QToolButton {
    background: transparent;
    border: 1px solid transparent;
    padding: 4px 6px;
    color: #000000;
    font-family: Tahoma, Arial;
    font-size: 8.5pt;
}
QToolButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #FFF6D0, stop:1 #FFE480);
    border: 1px solid #C49000;
}
QToolButton:pressed {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #FFE480, stop:1 #FFF6D0);
    border: 1px solid #806000;
}

/* ── Classic Buttons ──────────────────────────────────────── */
QPushButton {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #F7F5EE, stop:0.5 #ECE9D8, stop:1 #D5D1C6);
    border-top: 1px solid #FFFFFF;
    border-left: 1px solid #FFFFFF;
    border-right: 1px solid #706C60;
    border-bottom: 1px solid #706C60;
    font-family: Tahoma, Arial;
    font-size: 9pt;
    padding: 3px 10px;
    min-height: 22px;
    color: #000000;
}
QPushButton:pressed {
    border-top: 1px solid #706C60;
    border-left: 1px solid #706C60;
    border-right: 1px solid #FFFFFF;
    border-bottom: 1px solid #FFFFFF;
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #D5D1C6, stop:1 #F7F5EE);
    padding-left: 11px;
    padding-top: 4px;
}
QPushButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #FFFFFF, stop:1 #E0DCD0);
}
QPushButton:disabled {
    color: #888888;
    background: #ECE9D8;
    border: 1px solid #ACA899;
}
QPushButton:default {
    border: 2px solid #003399;
}

/* ── Input Fields ─────────────────────────────────────────── */
QLineEdit {
    background-color: #FFFFFF;
    border: 1px solid #7F9DB9;
    font-family: Tahoma, Arial;
    font-size: 9pt;
    padding: 2px 4px;
    color: #000000;
    selection-background-color: #316AC5;
    selection-color: #FFFFFF;
}
QLineEdit:focus {
    border: 1px solid #316AC5;
}
QLineEdit:disabled {
    background-color: #ECE9D8;
    color: #707070;
}

QComboBox {
    background-color: #FFFFFF;
    border: 1px solid #7F9DB9;
    font-family: Tahoma, Arial;
    font-size: 9pt;
    padding: 2px 4px;
    color: #000000;
}
QComboBox::drop-down {
    border-left: 1px solid #7F9DB9;
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #F4F2EC, stop:1 #D4D0C8);
    width: 18px;
}
QComboBox QAbstractItemView {
    background-color: #FFFFFF;
    border: 1px solid #716F64;
    selection-background-color: #316AC5;
    selection-color: #FFFFFF;
    color: #000000;
}

QDateEdit {
    background-color: #FFFFFF;
    border: 1px solid #7F9DB9;
    font-family: Tahoma, Arial;
    font-size: 9pt;
    padding: 2px 4px;
    color: #000000;
}
QDateEdit::drop-down {
    border-left: 1px solid #7F9DB9;
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #F4F2EC, stop:1 #D4D0C8);
    width: 18px;
}
QCalendarWidget {
    background-color: #FFFFFF;
    color: #000000;
    font-family: Tahoma, Arial;
    font-size: 9pt;
}

QSpinBox, QDoubleSpinBox {
    background-color: #FFFFFF;
    border: 1px solid #7F9DB9;
    font-family: Tahoma, Arial;
    font-size: 9pt;
    padding: 2px;
    color: #000000;
}

QTextEdit, QPlainTextEdit {
    background-color: #FFFFFF;
    border: 1px solid #7F9DB9;
    font-family: Tahoma, Arial;
    font-size: 9pt;
    color: #000000;
}

/* ── Tables (High Visibility, Windows XP Classic) ─────────── */
QTableWidget, QTableView {
    background-color: #FFFFFF;
    alternate-background-color: #F1F6FC;
    gridline-color: #D6D2C4;
    font-family: Tahoma, Arial;
    font-size: 9pt;
    color: #000000;
    border: 1px solid #7F9DB9;
    selection-background-color: #316AC5;
    selection-color: #FFFFFF;
}
QTableWidget::item {
    color: #000000;
    padding: 2px 4px;
    border-bottom: 1px solid #EBE7DA;
}
QTableWidget::item:selected {
    background-color: #316AC5;
    color: #FFFFFF;
}
QHeaderView {
    background: #ECE9D8;
    font-family: Tahoma, Arial;
    font-size: 9pt;
    color: #000000;
    border: none;
}
QHeaderView::section {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #FBF9F2, stop:0.5 #ECE9D8, stop:1 #DCD8CB);
    border-top: 1px solid #FFFFFF;
    border-left: 1px solid #FFFFFF;
    border-right: 1px solid #ACA899;
    border-bottom: 1px solid #ACA899;
    font-family: Tahoma, Arial;
    font-size: 9pt;
    font-weight: bold;
    color: #000000;
    padding: 4px 6px;
}
QHeaderView::section:pressed {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #DCD8CB, stop:1 #FBF9F2);
    border-top: 1px solid #ACA899;
    border-left: 1px solid #ACA899;
    border-right: 1px solid #FFFFFF;
    border-bottom: 1px solid #FFFFFF;
}

/* ── Labels ───────────────────────────────────────────────── */
QLabel {
    font-family: Tahoma, Arial;
    font-size: 9pt;
    color: #000000;
    background: transparent;
}

/* ── Group Box ────────────────────────────────────────────── */
QGroupBox {
    border: 1px solid #999587;
    margin-top: 10px;
    font-family: Tahoma, Arial;
    font-size: 9pt;
    font-weight: bold;
    background-color: #ECE9D8;
    color: #000000;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 8px;
    top: -2px;
    padding: 0 4px;
    color: #003399;
    background-color: #ECE9D8;
}

/* ── Status Bar with Sunken Panels ────────────────────────── */
QStatusBar {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #ECE9D8, stop:1 #DCD8CB);
    border-top: 1px solid #ACA899;
    font-family: Tahoma, Arial;
    font-size: 8.5pt;
    color: #000000;
}
QStatusBar QLabel {
    font-family: Tahoma, Arial;
    font-size: 8.5pt;
    color: #000000;
    padding: 1px 6px;
    border-top: 1px solid #ACA899;
    border-left: 1px solid #ACA899;
    border-right: 1px solid #FFFFFF;
    border-bottom: 1px solid #FFFFFF;
    background: #ECE9D8;
}

/* ── Scrollbars ────────────────────────────────────────────── */
QScrollBar:vertical {
    background: #D4D0C8;
    width: 16px;
    border: none;
    margin: 16px 0 16px 0;
}
QScrollBar::handle:vertical {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #FFFFFF, stop:0.3 #ECE9D8, stop:1 #C0BEAF);
    border-top: 1px solid #FFFFFF;
    border-left: 1px solid #FFFFFF;
    border-right: 1px solid #808080;
    border-bottom: 1px solid #808080;
    min-height: 20px;
}
QScrollBar::handle:vertical:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #FFFFFF, stop:0.3 #F0EDE0, stop:1 #C8C5B8);
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #F4F2EC, stop:1 #D4D0C8);
    border-top: 1px solid #FFFFFF;
    border-left: 1px solid #FFFFFF;
    border-right: 1px solid #808080;
    border-bottom: 1px solid #808080;
    height: 16px;
    subcontrol-origin: margin;
}
QScrollBar::add-line:vertical { subcontrol-position: bottom; }
QScrollBar::sub-line:vertical { subcontrol-position: top; }
QScrollBar:horizontal {
    background: #D4D0C8;
    height: 16px;
    margin: 0 16px 0 16px;
}
QScrollBar::handle:horizontal {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #FFFFFF, stop:0.3 #ECE9D8, stop:1 #C0BEAF);
    border-top: 1px solid #FFFFFF;
    border-left: 1px solid #FFFFFF;
    border-right: 1px solid #808080;
    border-bottom: 1px solid #808080;
    min-width: 20px;
}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #F4F2EC, stop:1 #D4D0C8);
    border-top: 1px solid #FFFFFF;
    border-left: 1px solid #FFFFFF;
    border-right: 1px solid #808080;
    border-bottom: 1px solid #808080;
    width: 16px;
    subcontrol-origin: margin;
}
QScrollBar::add-line:horizontal { subcontrol-position: right; }
QScrollBar::sub-line:horizontal { subcontrol-position: left; }

QScrollArea {
    border: none;
    background-color: #ECE9D8;
}

/* ── Splitter ──────────────────────────────────────────────── */
QSplitter::handle {
    background: #D4D0C8;
}
QSplitter::handle:horizontal {
    width: 4px;
    border-left: 1px solid #808080;
    border-right: 1px solid #FFFFFF;
}
QSplitter::handle:vertical {
    height: 4px;
    border-top: 1px solid #808080;
    border-bottom: 1px solid #FFFFFF;
}

/* ── Dialog ────────────────────────────────────────────────── */
QDialog {
    background-color: #ECE9D8;
}
"""

# ── Login Window ────────────────────────────────────────────────────────────────
LOGIN_BANNER_STYLE = """
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #0A246A, stop:0.4 #184CA0, stop:1 #0050A0);
"""

LOGIN_PANEL_STYLE = """
    background: #FFFFFF;
    border-top: 1px solid #FFFFFF;
    border-left: 1px solid #FFFFFF;
    border-right: 2px solid #808080;
    border-bottom: 2px solid #808080;
"""

LOGIN_TITLE_STYLE = """
    color: #FFFFFF;
    font-size: 26pt;
    font-weight: bold;
    font-family: Tahoma, Arial;
    background: transparent;
    letter-spacing: 2px;
"""

LOGIN_SUBTITLE_STYLE = """
    color: #B0D4FF;
    font-size: 9pt;
    font-family: Tahoma, Arial;
    background: transparent;
"""

LOGIN_HEADER_STYLE = """
    color: #003399;
    font-size: 11.5pt;
    font-weight: bold;
    font-family: Tahoma, Arial;
    background: transparent;
"""

# ── Sidebar ─────────────────────────────────────────────────────────────────────
SIDEBAR_STYLE = """
    background-color: #FFFFFF;
    border-right: 1px solid #999587;
"""

SIDEBAR_HEADER_STYLE = """
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #0A246A, stop:1 #003399);
    color: white;
    font-weight: bold;
    font-size: 9pt;
    font-family: Tahoma, Arial;
    padding: 6px 10px;
    border-bottom: 1px solid #001166;
"""

NAV_BUTTON_STYLE = """
QPushButton {
    background: transparent;
    border: 1px solid transparent;
    text-align: left;
    padding: 6px 12px;
    font-family: Tahoma, Arial;
    font-size: 9pt;
    color: #000000;
}
QPushButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #DDE8FF, stop:1 #EFF5FF);
    border: 1px solid #7F9DB9;
    color: #003399;
}
QPushButton:pressed {
    background: #BED4FA;
    border: 1px solid #316AC5;
}
QPushButton:checked {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #316AC5, stop:1 #5B8FD8);
    color: #FFFFFF;
    font-weight: bold;
    border: 1px solid #184CA0;
}
"""

LOGOUT_BUTTON_STYLE = """
QPushButton {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #F0C0C0, stop:1 #CC2020);
    border-top: 1px solid #FF9090;
    border-left: 1px solid #FF9090;
    border-right: 1px solid #700000;
    border-bottom: 1px solid #700000;
    color: #FFFFFF;
    font-family: Tahoma, Arial;
    font-size: 9pt;
    font-weight: bold;
    padding: 4px 10px;
    min-height: 22px;
    text-align: left;
}
QPushButton:pressed {
    border-top: 1px solid #700000;
    border-left: 1px solid #700000;
    border-right: 1px solid #FF9090;
    border-bottom: 1px solid #FF9090;
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #CC2020, stop:1 #F0C0C0);
}
QPushButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #FFD0D0, stop:1 #DD2020);
}
"""

SECTION_HEADER_STYLE = """
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #0A246A, stop:0.5 #003399, stop:1 #0050A0);
    color: white;
    font-weight: bold;
    font-size: 10.5pt;
    font-family: Tahoma, Arial;
    padding: 6px 12px;
    border-bottom: 2px solid #001166;
"""

BLUE_BUTTON_STYLE = """
QPushButton {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #4E87D0, stop:1 #1B4FA2);
    border-top: 1px solid #82B0FF;
    border-left: 1px solid #82B0FF;
    border-right: 1px solid #002277;
    border-bottom: 1px solid #002277;
    color: white;
    font-family: Tahoma, Arial;
    font-size: 9pt;
    font-weight: bold;
    padding: 3px 12px;
    min-height: 23px;
}
QPushButton:pressed {
    border-top: 1px solid #002277;
    border-left: 1px solid #002277;
    border-right: 1px solid #82B0FF;
    border-bottom: 1px solid #82B0FF;
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #1B4FA2, stop:1 #4E87D0);
}
QPushButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #649DE8, stop:1 #245CB3);
}
"""

TOOLBAR_STYLE = """
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #F6F4ED, stop:0.5 #ECE9D8, stop:1 #D9D4C7);
    border-bottom: 1px solid #999587;
    border-top: 1px solid #FFFFFF;
"""

SUBHEADER_STYLE = """
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #F4F2EC, stop:1 #DCD8CB);
    border-top: 1px solid #FFFFFF;
    border-left: 1px solid #FFFFFF;
    border-right: 1px solid #999587;
    border-bottom: 1px solid #999587;
    font-family: Tahoma, Arial;
    font-size: 9pt;
    font-weight: bold;
    color: #003399;
    padding-left: 8px;
"""
