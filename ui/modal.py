import sys
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QWidget, QGraphicsDropShadowEffect, QFrame, QApplication, QMessageBox
)
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QColor, QFont

class CustomModal(QDialog):
    """
    Modern minimalist frameless modal dialog with subtle fade-in animation,
    clean iconography, and glowing borders.
    """
    def __init__(self, parent=None, title="Notification", message="",
                 modal_type="info", confirm_mode=False, ok_text="OK",
                 cancel_text="Batal", is_danger=False):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setModal(True)

        self.modal_type = modal_type
        self.confirm_mode = confirm_mode
        self.is_danger = is_danger
        self.result_value = False

        self.init_ui(title, message, ok_text, cancel_text)

        # Center on parent window if available
        if parent:
            try:
                parent_window = parent.window()
                p_geom = parent_window.geometry()
                self.adjustSize()
                x = p_geom.x() + (p_geom.width() - self.width()) // 2
                y = p_geom.y() + (p_geom.height() - self.height()) // 2
                self.move(max(10, x), max(10, y))
            except Exception:
                pass

    def init_ui(self, title_text: str, message_text: str, ok_text: str, cancel_text: str):
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(18, 18, 18, 18)

        # Card container (Pure White Minimalist)
        self.card = QFrame()
        self.card.setObjectName("modalCard")
        self.card.setStyleSheet("""
            QFrame#modalCard {
                background-color: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 14px;
            }
        """)

        # Clean soft drop shadow
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(28)
        shadow.setColor(QColor(15, 23, 42, 50))
        shadow.setOffset(0, 8)
        self.card.setGraphicsEffect(shadow)

        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(22, 22, 22, 18)
        card_layout.setSpacing(12)

        # Header with icon and title
        header = QHBoxLayout()
        header.setSpacing(12)

        # Type configuration
        type_configs = {
            "info": {"icon": "ℹ", "color": "#2563eb", "bg": "#eff6ff", "border": "#bfdbfe"},
            "success": {"icon": "✓", "color": "#16a34a", "bg": "#f0fdf4", "border": "#bbf7d0"},
            "warning": {"icon": "⚠", "color": "#d97706", "bg": "#fffbeb", "border": "#fde68a"},
            "critical": {"icon": "✕", "color": "#dc2626", "bg": "#fef2f2", "border": "#fecaca"},
            "question": {"icon": "?", "color": "#7c3aed", "bg": "#f5f3ff", "border": "#ddd6fe"},
        }
        cfg = type_configs.get(self.modal_type, type_configs["info"])

        icon_lbl = QLabel(cfg["icon"])
        icon_lbl.setFixedSize(34, 34)
        icon_lbl.setAlignment(Qt.AlignCenter)
        icon_lbl.setStyleSheet(f"""
            QLabel {{
                background-color: {cfg['bg']};
                color: {cfg['color']};
                border: 1px solid {cfg['border']};
                border-radius: 17px;
                font-size: 15px;
                font-weight: bold;
            }}
        """)
        header.addWidget(icon_lbl)

        title_lbl = QLabel(title_text)
        title_lbl.setStyleSheet("color: #0f172a; font-size: 15px; font-weight: 700;")
        header.addWidget(title_lbl, 1)

        card_layout.addLayout(header)

        # Message body (support both real and escaped newlines)
        clean_msg = message_text.replace("\\n", "\n")
        msg_lbl = QLabel(clean_msg)
        msg_lbl.setWordWrap(True)
        msg_lbl.setStyleSheet("color: #475569; font-size: 13px; line-height: 1.4; padding: 2px 0;")
        msg_lbl.setMinimumWidth(320)
        msg_lbl.setMaximumWidth(450)
        card_layout.addWidget(msg_lbl)

        # Button row
        btn_row = QHBoxLayout()
        btn_row.setContentsMargins(0, 8, 0, 0)
        btn_row.setSpacing(10)
        btn_row.addStretch()

        if self.confirm_mode:
            btn_cancel = QPushButton(cancel_text)
            btn_cancel.setFixedHeight(34)
            btn_cancel.setFixedWidth(85)
            btn_cancel.setStyleSheet("""
                QPushButton {
                    background-color: #ffffff;
                    color: #475569;
                    border: 1px solid #cbd5e1;
                    border-radius: 6px;
                    font-weight: 500;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #f8fafc;
                    border-color: #94a3b8;
                    color: #0f172a;
                }
            """)
            btn_cancel.clicked.connect(self.on_cancel)
            btn_row.addWidget(btn_cancel)

        # OK / Action button
        btn_ok = QPushButton(ok_text)
        btn_ok.setFixedHeight(34)
        btn_ok.setFixedWidth(95 if not self.confirm_mode else 90)

        if self.is_danger or self.modal_type == "critical":
            btn_ok.setStyleSheet("""
                QPushButton {
                    background-color: #dc2626;
                    color: #ffffff;
                    border: 1px solid #dc2626;
                    border-radius: 6px;
                    font-weight: 600;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #b91c1c;
                    border-color: #991b1b;
                }
            """)
        else:
            btn_ok.setStyleSheet("""
                QPushButton {
                    background-color: #2563eb;
                    color: #ffffff;
                    border: 1px solid #2563eb;
                    border-radius: 6px;
                    font-weight: 600;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #1d4ed8;
                    border-color: #1e40af;
                }
            """)

        btn_ok.clicked.connect(self.on_ok)
        btn_row.addWidget(btn_ok)

        card_layout.addLayout(btn_row)
        outer_layout.addWidget(self.card)

    def on_ok(self):
        self.result_value = True
        self.close_with_fade()

    def on_cancel(self):
        self.result_value = False
        self.close_with_fade()

    def showEvent(self, event):
        super().showEvent(event)
        # Subtle, clean fade-in animation
        self.anim = QPropertyAnimation(self, b"windowOpacity")
        self.anim.setDuration(150)
        self.anim.setStartValue(0.0)
        self.anim.setEndValue(1.0)
        self.anim.setEasingCurve(QEasingCurve.OutCubic)
        self.anim.start()

    def close_with_fade(self):
        self.anim_close = QPropertyAnimation(self, b"windowOpacity")
        self.anim_close.setDuration(110)
        self.anim_close.setStartValue(1.0)
        self.anim_close.setEndValue(0.0)
        self.anim_close.setEasingCurve(QEasingCurve.InCubic)
        self.anim_close.finished.connect(self.accept if self.result_value else self.reject)
        self.anim_close.start()


class Modal:
    """Convenient static interface for showing minimalist in-app modals."""

    @staticmethod
    def alert(parent, title: str, message: str, modal_type: str = "info", ok_text: str = "OK"):
        dlg = CustomModal(parent, title=title, message=message, modal_type=modal_type,
                          confirm_mode=False, ok_text=ok_text)
        dlg.exec()

    @staticmethod
    def info(parent, title: str, message: str, ok_text: str = "OK"):
        Modal.alert(parent, title, message, modal_type="info", ok_text=ok_text)

    @staticmethod
    def success(parent, title: str, message: str, ok_text: str = "OK"):
        Modal.alert(parent, title, message, modal_type="success", ok_text=ok_text)

    @staticmethod
    def warning(parent, title: str, message: str, ok_text: str = "Mengerti"):
        Modal.alert(parent, title, message, modal_type="warning", ok_text=ok_text)

    @staticmethod
    def error(parent, title: str, message: str, ok_text: str = "Tutup"):
        Modal.alert(parent, title, message, modal_type="critical", ok_text=ok_text)

    @staticmethod
    def confirm(parent, title: str, message: str, ok_text: str = "Ya, Lanjutkan",
                cancel_text: str = "Batal", is_danger: bool = False) -> bool:
        dlg = CustomModal(parent, title=title, message=message, modal_type="question" if not is_danger else "critical",
                          confirm_mode=True, ok_text=ok_text, cancel_text=cancel_text, is_danger=is_danger)
        dlg.exec()
        return dlg.result_value


def _modal_information(parent, title: str, text: str, *args, **kwargs):
    Modal.info(parent, title, text)
    return QMessageBox.StandardButton.Ok

def _modal_warning(parent, title: str, text: str, *args, **kwargs):
    # Check if used as a confirmation question
    check_args = list(args) + list(kwargs.values())
    if any(btn in [QMessageBox.StandardButton.Yes, 16384, QMessageBox.StandardButton.No, 65536] for btn in check_args):
        ans = Modal.confirm(parent, title, text, ok_text="Ya, Lanjutkan", cancel_text="Batal", is_danger=True)
        return QMessageBox.StandardButton.Yes if ans else QMessageBox.StandardButton.No
    Modal.warning(parent, title, text)
    return QMessageBox.StandardButton.Ok

def _modal_critical(parent, title: str, text: str, *args, **kwargs):
    check_args = list(args) + list(kwargs.values())
    if any(btn in [QMessageBox.StandardButton.Yes, 16384, QMessageBox.StandardButton.No, 65536] for btn in check_args):
        ans = Modal.confirm(parent, title, text, ok_text="Ya, Lanjutkan", cancel_text="Batal", is_danger=True)
        return QMessageBox.StandardButton.Yes if ans else QMessageBox.StandardButton.No
    Modal.error(parent, title, text)
    return QMessageBox.StandardButton.Ok

def _modal_question(parent, title: str, text: str, *args, **kwargs):
    ans = Modal.confirm(parent, title, text, ok_text="Ya", cancel_text="Batal")
    return QMessageBox.StandardButton.Yes if ans else QMessageBox.StandardButton.No

def patch_qmessagebox():
    """Globally redirects all QMessageBox calls to our sleek in-app ModalDialog."""
    QMessageBox.information = _modal_information
    QMessageBox.warning = _modal_warning
    QMessageBox.critical = _modal_critical
    QMessageBox.question = _modal_question

# Apply global patch automatically on import
patch_qmessagebox()
