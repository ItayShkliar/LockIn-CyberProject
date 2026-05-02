"""
Main Window View — Sidebar + content area shell.
Premium sidebar with logo, minimal navigation icons, and smooth active states.
"""
import os
import sys
from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout,
                             QPushButton, QStackedWidget, QLabel, QFrame)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPixmap


def _resource_path(filename: str) -> str:
    if getattr(sys, 'frozen', False):
        base = sys._MEIPASS
    else:
        base = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
    return os.path.join(base, 'resources', filename)


class MainWindowView(QWidget):
    def __init__(self):
        super().__init__()
        self._init_ui()

    def _init_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ────────────────────────────────────
        # 1. SIDEBAR
        # ────────────────────────────────────
        sidebar = QWidget()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(220)

        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(16, 24, 16, 24)
        sidebar_layout.setSpacing(4)

        # Logo area
        logo_container = QWidget()
        logo_container.setObjectName("LogoContainer")
        logo_layout = QHBoxLayout(logo_container)
        logo_layout.setContentsMargins(8, 0, 8, 0)
        logo_layout.setSpacing(10)

        logo_path = _resource_path("logo.png")
        if os.path.exists(logo_path):
            logo_img = QLabel()
            pm = QPixmap(logo_path).scaled(32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_img.setPixmap(pm)
            logo_img.setFixedSize(32, 32)
            logo_img.setStyleSheet("background: transparent; border: none;")
            logo_layout.addWidget(logo_img)

        logo_text_container = QVBoxLayout()
        logo_text_container.setSpacing(0)
        logo_text = QLabel("LOCK IN")
        logo_text.setObjectName("LogoText")
        logo_text.setStyleSheet("background: transparent;")
        logo_text_container.addWidget(logo_text)

        logo_sub = QLabel("PRODUCTIVITY")
        logo_sub.setObjectName("LogoSubtext")
        logo_sub.setStyleSheet("background: transparent;")
        logo_text_container.addWidget(logo_sub)
        logo_layout.addLayout(logo_text_container)
        logo_layout.addStretch()

        sidebar_layout.addWidget(logo_container)
        sidebar_layout.addSpacing(28)

        # Section label
        nav_label = QLabel("MENU")
        nav_label.setObjectName("SectionHeader")
        nav_label.setStyleSheet("padding-left: 12px; margin-bottom: 6px; background: transparent;")
        sidebar_layout.addWidget(nav_label)

        # Navigation Buttons
        self.nav_buttons = {}
        nav_items = [
            ("home_btn",         "🏠  Home"),
            ("focus_btn",        "⏱  Focus"),
            ("competitions_btn", "🏆  Competitions"),
            ("leaderboard_btn",  "📊  Leaderboards"),
            ("stats_btn",        "📈  History"),
            ("settings_btn",     "👤  My Profile"),
        ]

        for btn_name, text in nav_items:
            btn = QPushButton(text)
            btn.setObjectName("NavBtn")
            btn.setFixedHeight(42)
            btn.setCursor(Qt.PointingHandCursor)
            self.nav_buttons[btn_name] = btn
            sidebar_layout.addWidget(btn)

        sidebar_layout.addStretch()

        # Divider above logout
        divider = QFrame()
        divider.setFixedHeight(1)
        divider.setStyleSheet("background-color: rgba(51, 65, 85, 0.2); border: none;")
        sidebar_layout.addWidget(divider)
        sidebar_layout.addSpacing(12)

        # Logout Button
        self.logout_btn = QPushButton("↩  Sign Out")
        self.logout_btn.setProperty("theme", "ghost")
        self.logout_btn.setFixedHeight(40)
        self.logout_btn.setCursor(Qt.PointingHandCursor)
        self.logout_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: 1px solid rgba(239, 68, 68, 0.2);
                border-radius: 10px;
                color: #64748b;
                font-weight: 600;
                font-size: 12px;
            }
            QPushButton:hover {
                background: rgba(239, 68, 68, 0.08);
                color: #f87171;
                border-color: rgba(239, 68, 68, 0.3);
            }
        """)
        sidebar_layout.addWidget(self.logout_btn)

        # ────────────────────────────────────
        # 2. CONTENT AREA
        # ────────────────────────────────────
        self.content_area = QStackedWidget()
        self.content_area.setObjectName("ContentArea")

        main_layout.addWidget(sidebar)
        main_layout.addWidget(self.content_area)

    def add_tab(self, widget: QWidget):
        self.content_area.addWidget(widget)

    def switch_tab(self, index: int):
        for i, btn in enumerate(self.nav_buttons.values()):
            btn.setProperty("active", i == index)
            btn.style().unpolish(btn)
            btn.style().polish(btn)

        self.content_area.setCurrentIndex(index)