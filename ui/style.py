"""
Modern Minimalist White Theme (Compact & Refined Edition).
Features ultra-clean borders, compact padding/margins, subtle hover glow,
and legible 12px typography.
"""

LIGHT_THEME_QSS = """
/* Global Window & Fonts (Compact Edition) */
QWidget {
    background-color: #ffffff;
    color: #0f172a;
    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
    font-size: 11px;
    selection-background-color: #3b82f6;
    selection-color: #ffffff;
}

/* Main Window Background */
QMainWindow {
    background-color: #f8fafc;
}

/* Content Area Background */
QScrollArea, QScrollArea > QWidget > QWidget {
    background-color: #f8fafc;
}

/* Sidebar & Navigation (Compact & Sleek) */
#sidebar {
    background-color: #ffffff;
    border-right: 1px solid #e2e8f0;
    min-width: 185px;
    max-width: 195px;
}

#sidebar QLabel#appTitle {
    color: #0f172a;
    font-size: 13px;
    font-weight: bold;
    padding: 8px 6px;
}

#sidebar QPushButton {
    background-color: transparent;
    color: #475569;
    text-align: left;
    padding: 5px 10px;
    border: 1px solid transparent;
    border-radius: 5px;
    margin: 1px 3px;
    font-size: 11px;
    font-weight: 500;
}

#sidebar QPushButton:hover {
    background-color: #f1f5f9;
    border-color: #e2e8f0;
    color: #0f172a;
}

#sidebar QPushButton:checked, #sidebar QPushButton[active="true"] {
    background-color: #2563eb;
    border-color: #2563eb;
    color: #ffffff;
    font-weight: 600;
}

/* Top Header Bar */
#topHeader {
    background-color: #ffffff;
    border-bottom: 1px solid #e2e8f0;
    padding: 4px 10px;
}

/* Cards & Containers (Compact Minimalist White) */
QFrame[card="true"], QGroupBox {
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 6px;
    padding-top: 14px;
    padding-bottom: 6px;
    padding-left: 8px;
    padding-right: 8px;
    margin-top: 6px;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 1px 6px;
    color: #1e293b;
    font-weight: 600;
    font-size: 10px;
    background-color: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 3px;
    left: 8px;
    top: 1px;
}

/* Standard Buttons (Compact & Refined) */
QPushButton {
    background-color: #ffffff;
    color: #1e293b;
    border: 1px solid #cbd5e1;
    border-radius: 4px;
    padding: 3px 8px;
    min-height: 22px;
    font-weight: 500;
    font-size: 11px;
}

/* Subtle glow / border highlight on hover without heavy animation */
QPushButton:hover {
    background-color: #f8fafc;
    border-color: #3b82f6;
    color: #1d4ed8;
}

QPushButton:pressed {
    background-color: #f1f5f9;
    border-color: #2563eb;
}

QPushButton:disabled {
    background-color: #f8fafc;
    color: #94a3b8;
    border-color: #e2e8f0;
}

/* Primary Button */
QPushButton[primary="true"] {
    background-color: #2563eb;
    border: 1px solid #2563eb;
    color: #ffffff;
    font-weight: 600;
}

QPushButton[primary="true"]:hover {
    background-color: #1d4ed8;
    border-color: #1e40af;
    color: #ffffff;
}

QPushButton[primary="true"]:pressed {
    background-color: #1e40af;
}

/* Success Button */
QPushButton[success="true"] {
    background-color: #16a34a;
    border: 1px solid #16a34a;
    color: #ffffff;
    font-weight: 600;
}

QPushButton[success="true"]:hover {
    background-color: #15803d;
    border-color: #166534;
    color: #ffffff;
}

/* Danger Button */
QPushButton[danger="true"] {
    background-color: #dc2626;
    border: 1px solid #dc2626;
    color: #ffffff;
    font-weight: 600;
}

QPushButton[danger="true"]:hover {
    background-color: #b91c1c;
    border-color: #991b1b;
    color: #ffffff;
}

/* LineEdit, SpinBox, ComboBox (Compact) */
QLineEdit, QSpinBox, QComboBox {
    background-color: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 4px;
    padding: 2px 6px;
    min-height: 23px;
    color: #0f172a;
    font-size: 11px;
}

QLineEdit:hover, QSpinBox:hover, QComboBox:hover {
    border-color: #94a3b8;
}

QLineEdit:focus, QSpinBox:focus, QComboBox:focus {
    border: 1px solid #2563eb;
    background-color: #ffffff;
}

QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 18px;
    border-left: 1px solid #e2e8f0;
}

QComboBox QAbstractItemView {
    background-color: #ffffff;
    color: #0f172a;
    border: 1px solid #cbd5e1;
    border-radius: 4px;
    selection-background-color: #eff6ff;
    selection-color: #1d4ed8;
    padding: 2px;
    font-size: 11px;
}

/* CheckBoxes, RadioButtons & Table Indicators (Compact) */
QCheckBox, QRadioButton {
    color: #1e293b;
    font-size: 11px;
    spacing: 5px;
}

QCheckBox::indicator, QRadioButton::indicator, QTableWidget::indicator, QTableView::indicator {
    width: 14px;
    height: 14px;
    border: 1px solid #cbd5e1;
    border-radius: 3px;
    background-color: #ffffff;
}

QCheckBox::indicator:hover, QRadioButton::indicator:hover, QTableWidget::indicator:hover, QTableView::indicator:hover {
    border-color: #3b82f6;
}

QCheckBox::indicator:checked, QTableWidget::indicator:checked, QTableView::indicator:checked {
    background-color: #2563eb;
    border-color: #2563eb;
    image: url(data/check.png);
}

QRadioButton::indicator {
    border-radius: 7px;
}

QRadioButton::indicator:checked {
    background-color: #2563eb;
    border-color: #2563eb;
    image: none;
}

/* Tables (Compact) */
QTableWidget {
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 5px;
    gridline-color: #f1f5f9;
    color: #0f172a;
    font-size: 11px;
    alternate-background-color: #fcfcfd;
}

QTableWidget::item {
    padding: 3px 5px;
    border-bottom: 1px solid #f1f5f9;
}

QTableWidget::item:selected {
    background-color: #eff6ff;
    color: #1d4ed8;
    font-weight: 500;
}

QHeaderView::section {
    background-color: #f8fafc;
    color: #475569;
    padding: 4px 6px;
    border: none;
    border-bottom: 1px solid #e2e8f0;
    font-weight: 600;
    font-size: 10px;
}

/* Tab Widget (Compact & Modern) */
QTabWidget::pane {
    border: 1px solid #e2e8f0;
    background-color: #ffffff;
    border-radius: 5px;
    padding: 6px;
}

QTabBar::tab {
    background-color: #f8fafc;
    color: #64748b;
    padding: 4px 12px;
    margin-right: 2px;
    border: 1px solid #e2e8f0;
    border-bottom: none;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
    font-size: 11px;
}

QTabBar::tab:selected {
    background-color: #ffffff;
    color: #2563eb;
    font-weight: bold;
    border-color: #cbd5e1;
    border-bottom: 1px solid #ffffff;
}

QTabBar::tab:hover:!selected {
    background-color: #f1f5f9;
    color: #0f172a;
}

/* Scrollbars */
QScrollBar:vertical {
    background: #f8fafc;
    width: 6px;
    margin: 0;
    border-radius: 3px;
}

QScrollBar::handle:vertical {
    background: #cbd5e1;
    min-height: 18px;
    border-radius: 3px;
}

QScrollBar::handle:vertical:hover {
    background: #94a3b8;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    background: #f8fafc;
    height: 6px;
    margin: 0;
    border-radius: 3px;
}

QScrollBar::handle:horizontal {
    background: #cbd5e1;
    min-width: 18px;
    border-radius: 3px;
}

/* Progress Bar */
QProgressBar {
    background-color: #f1f5f9;
    border: 1px solid #e2e8f0;
    border-radius: 3px;
    text-align: center;
    color: #0f172a;
    font-weight: bold;
    font-size: 9px;
    height: 12px;
}

QProgressBar::chunk {
    background-color: #2563eb;
    border-radius: 2px;
}

/* TextEdit / Console Log Area */
QTextEdit, QPlainTextEdit {
    background-color: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 4px;
    color: #0f172a;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 11px;
    padding: 4px;
}

QTextEdit:focus, QPlainTextEdit:focus {
    border-color: #2563eb;
}

/* Status Bar */
QStatusBar {
    background-color: #ffffff;
    border-top: 1px solid #e2e8f0;
    color: #64748b;
    font-size: 10px;
    padding: 2px;
}

/* Badges & Status Pills (Compact) */
QLabel[badge="online"], QLabel[badge="device"] {
    background-color: #dcfce7;
    color: #15803d;
    border: 1px solid #bbf7d0;
    padding: 2px 8px;
    min-width: 60px;
    border-radius: 8px;
    font-weight: bold;
    font-size: 10px;
}

QLabel[badge="unauthorized"], QLabel[badge="offline"] {
    background-color: #fee2e2;
    color: #b91c1c;
    border: 1px solid #fecaca;
    padding: 2px 8px;
    min-width: 60px;
    border-radius: 8px;
    font-weight: bold;
    font-size: 10px;
}

QLabel[badge="fastboot"] {
    background-color: #fef3c7;
    color: #b45309;
    border: 1px solid #fde68a;
    padding: 2px 8px;
    min-width: 60px;
    border-radius: 8px;
    font-weight: bold;
    font-size: 10px;
}
"""

# Backwards compatibility alias
DARK_THEME_QSS = LIGHT_THEME_QSS

from PySide6.QtWidgets import QPushButton

def styled_btn(text: str, role: str = "") -> QPushButton:
    """Helper to create a QPushButton with custom QSS property role (e.g. 'primary', 'danger', 'success')."""
    btn = QPushButton(text)
    if role:
        btn.setProperty(role, "true")
    return btn
