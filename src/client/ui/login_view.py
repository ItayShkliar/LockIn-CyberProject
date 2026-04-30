"""
Login View — Premium dark login screen with background image and logo.
"""
import os
import sys
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QLineEdit,
                             QPushButton, QFrame, QHBoxLayout, QGraphicsDropShadowEffect)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPixmap, QPalette, QBrush, QColor, QFont


def _resource_path(filename: str) -> str:
    """Resolves a path inside the resources/ folder, works for both dev and PyInstaller."""
    if getattr(sys, 'frozen', False):
        base = sys._MEIPASS
    else:
        base = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
    return os.path.join(base, 'resources', filename)


class LoginView(QWidget):
    def __init__(self):
        super().__init__()
        self.is_login_mode = True
        self._init_ui()

    def _init_ui(self):
        # ── Background image ──
        self.setAutoFillBackground(True)
        bg_path = _resource_path("login_bg.png")
        if os.path.exists(bg_path):
            palette = self.palette()
            bg = QPixmap(bg_path)
            palette.setBrush(QPalette.Window, QBrush(bg.scaled(
                1920, 1080, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation
            )))
            self.setPalette(palette)

        # ── Outer layout centers the card ──
        outer_layout = QVBoxLayout(self)
        outer_layout.setAlignment(Qt.AlignCenter)

        # ── Glass card ──
        self.card = QFrame()
        self.card.setObjectName("Card")
        self.card.setFixedWidth(400)
        self.card.setStyleSheet("""
            QFrame#Card {
                background-color: rgba(10, 15, 30, 0.85);
                border-radius: 20px;
                border: 1px solid rgba(59, 130, 246, 0.12);
            }
        """)

        # Subtle glow shadow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(60)
        shadow.setColor(QColor(59, 130, 246, 30))
        shadow.setOffset(0, 4)
        self.card.setGraphicsEffect(shadow)

        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(36, 44, 36, 36)
        card_layout.setSpacing(0)

        # ── Logo ──
        logo_path = _resource_path("logo.png")
        if os.path.exists(logo_path):
            logo_label = QLabel()
            logo_pixmap = QPixmap(logo_path).scaled(
                64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            logo_label.setPixmap(logo_pixmap)
            logo_label.setAlignment(Qt.AlignCenter)
            logo_label.setStyleSheet("background: transparent; border: none; margin-bottom: 4px;")
            card_layout.addWidget(logo_label)

        # ── Title ──
        title = QLabel("Lock In")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            font-size: 26px;
            font-weight: 800;
            color: #f8fafc;
            letter-spacing: 1px;
            margin-top: 8px;
            margin-bottom: 2px;
            background: transparent;
        """)
        card_layout.addWidget(title)

        # ── Subtitle ──
        self._subtitle = QLabel("Welcome back")
        self._subtitle.setAlignment(Qt.AlignCenter)
        self._subtitle.setWordWrap(True)
        self._subtitle.setStyleSheet("""
            font-size: 13px;
            color: #475569;
            font-weight: 500;
            margin-bottom: 24px;
            background: transparent;
        """)
        card_layout.addWidget(self._subtitle)

        # ── Inputs ──
        self._username_input = self._make_input("Username")
        card_layout.addWidget(self._username_input)
        card_layout.addSpacing(10)

        self._email_input = self._make_input("Email")
        self._email_input.hide()
        card_layout.addWidget(self._email_input)

        self._password_input = self._make_input("Password", is_password=True)
        card_layout.addWidget(self._password_input)
        card_layout.addSpacing(20)

        # ── Action Buttons ──
        self._login_btn = QPushButton("Sign In")
        self._login_btn.setProperty("theme", "primary")
        self._login_btn.setFixedHeight(46)
        self._login_btn.setCursor(Qt.PointingHandCursor)
        self._login_btn.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                font-weight: 700;
                border-radius: 12px;
                letter-spacing: 0.5px;
            }
        """)
        card_layout.addWidget(self._login_btn)

        self._register_btn = QPushButton("Create Account")
        self._register_btn.setProperty("theme", "success")
        self._register_btn.setFixedHeight(46)
        self._register_btn.setCursor(Qt.PointingHandCursor)
        self._register_btn.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                font-weight: 700;
                border-radius: 12px;
                letter-spacing: 0.5px;
            }
        """)
        self._register_btn.hide()
        card_layout.addWidget(self._register_btn)

        card_layout.addSpacing(16)

        # ── Divider ──
        divider = QFrame()
        divider.setFixedHeight(1)
        divider.setStyleSheet("background-color: rgba(51, 65, 85, 0.3); border: none;")
        card_layout.addWidget(divider)

        card_layout.addSpacing(12)

        # ── Mode Switcher ──
        self._switch_mode_btn = QPushButton("Don't have an account? Register")
        self._switch_mode_btn.setCursor(Qt.PointingHandCursor)
        self._switch_mode_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                color: #475569;
                font-size: 12px;
                font-weight: 500;
                padding: 4px;
            }
            QPushButton:hover {
                color: #60a5fa;
            }
        """)
        self._switch_mode_btn.clicked.connect(self._toggle_mode)
        card_layout.addWidget(self._switch_mode_btn)

        outer_layout.addWidget(self.card)

    def _make_input(self, placeholder: str, is_password: bool = False) -> QLineEdit:
        inp = QLineEdit()
        inp.setPlaceholderText(placeholder)
        inp.setFixedHeight(44)
        if is_password:
            inp.setEchoMode(QLineEdit.Password)
        inp.setStyleSheet("""
            QLineEdit {
                background-color: rgba(15, 23, 42, 0.5);
                border: 1px solid rgba(51, 65, 85, 0.35);
                border-radius: 12px;
                padding: 0 16px;
                color: #e2e8f0;
                font-size: 13px;
            }
            QLineEdit:focus {
                border-color: rgba(59, 130, 246, 0.5);
                background-color: rgba(15, 23, 42, 0.7);
            }
        """)
        return inp

    def _toggle_mode(self):
        if self.is_login_mode:
            self._subtitle.setText("Create a new account")
            self._email_input.show()
            self._login_btn.hide()
            self._register_btn.show()
            self._switch_mode_btn.setText("Already have an account? Sign in")
            self.is_login_mode = False
        else:
            self._subtitle.setText("Welcome back")
            self._email_input.hide()
            self._login_btn.show()
            self._register_btn.hide()
            self._switch_mode_btn.setText("Don't have an account? Register")
            self.is_login_mode = True

    def resizeEvent(self, event):
        """Re-tile the background when the window resizes."""
        super().resizeEvent(event)
        bg_path = _resource_path("login_bg.png")
        if os.path.exists(bg_path):
            palette = self.palette()
            bg = QPixmap(bg_path)
            palette.setBrush(QPalette.Window, QBrush(bg.scaled(
                self.width(), self.height(),
                Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation
            )))
            self.setPalette(palette)