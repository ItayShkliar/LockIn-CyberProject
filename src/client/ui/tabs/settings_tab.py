"""
Settings Tab — Blocked apps, connection, profile, and achievements.
"""
import json
import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QMessageBox, QScrollArea,
    QTabWidget, QFrame, QSpinBox, QGraphicsDropShadowEffect
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor

CONFIG_FILE = "lockin_config.json"

class SettingsTab(QWidget):
    def __init__(self, network_client=None):
        super().__init__()
        self.network_client = network_client
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(44, 44, 44, 44)
        layout.setSpacing(24)

        title = QLabel("MY PROFILE")
        title.setObjectName("Title")
        layout.addWidget(title)

        subtitle = QLabel("View your profile statistics and achievements.")
        subtitle.setStyleSheet("color: #475569; font-size: 13px; margin-bottom: 4px;")
        layout.addWidget(subtitle)

        self.sub_tabs = QTabWidget()
        self.sub_tabs.addTab(self._build_profile_tab(), "My Profile")
        self.sub_tabs.addTab(self._build_achievements_tab(), "Achievements")

        layout.addWidget(self.sub_tabs)

    def _read_config(self) -> dict:
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f: return json.load(f)
            except Exception: pass
        return {"blocked_apps": []}

    def _write_config(self, config: dict):
        try:
            with open(CONFIG_FILE, "w") as f: json.dump(config, f, indent=4)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not save: {e}")

    def _build_connection_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(14)

        header = QLabel("SERVER CONNECTION")
        header.setObjectName("SectionHeader")
        layout.addWidget(header)

        host_lbl = QLabel("Host")
        host_lbl.setStyleSheet("font-size: 11px; color: #475569; font-weight: 600; margin-top: 4px;")
        layout.addWidget(host_lbl)
        self.host_input = QLineEdit()
        self.host_input.setFixedHeight(38)
        layout.addWidget(self.host_input)

        port_lbl = QLabel("Port")
        port_lbl.setStyleSheet("font-size: 11px; color: #475569; font-weight: 600; margin-top: 4px;")
        layout.addWidget(port_lbl)
        self.port_input = QSpinBox()
        self.port_input.setRange(1, 65535)
        self.port_input.setFixedHeight(38)
        layout.addWidget(self.port_input)

        config = self._read_config()
        self.host_input.setText(config.get("server_host", "127.0.0.1"))
        self.port_input.setValue(config.get("server_port", 65432))

        save_btn = QPushButton("Save Settings")
        save_btn.setProperty("theme", "primary")
        save_btn.setFixedHeight(40)
        save_btn.setCursor(Qt.PointingHandCursor)
        save_btn.clicked.connect(self._save_connection)
        layout.addWidget(save_btn)

        self.conn_status_lbl = QLabel("")
        self.conn_status_lbl.setStyleSheet("color: #475569; font-size: 12px;")
        layout.addWidget(self.conn_status_lbl)
        layout.addStretch()
        return widget

    def _save_connection(self):
        config = self._read_config()
        config["server_host"] = self.host_input.text().strip()
        config["server_port"] = self.port_input.value()
        self._write_config(config)
        QMessageBox.information(self, "Saved", "Settings saved. Please restart the app.")

    def _build_profile_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        header = QLabel("YOUR PROFILE")
        header.setObjectName("SectionHeader")
        layout.addWidget(header)

        self.profile_card = QFrame()
        self.profile_card.setObjectName("Card")
        self.profile_layout = QVBoxLayout(self.profile_card)
        self.profile_layout.setContentsMargins(24, 20, 24, 20)
        self.profile_layout.setSpacing(10)
        layout.addWidget(self.profile_card)
        layout.addStretch()
        return widget

    def _load_profile(self):
        for i in reversed(range(self.profile_layout.count())):
            w = self.profile_layout.itemAt(i).widget()
            if w: w.deleteLater()

        if not self.network_client or not self.network_client.logged_in_user_id:
            lbl = QLabel("Not logged in.")
            lbl.setStyleSheet("color: #334155;")
            self.profile_layout.addWidget(lbl)
            return

        response = self.network_client.get_user_profile()
        if response.get("status") != "success":
            lbl = QLabel("Failed to load profile.")
            lbl.setStyleSheet("color: #f87171;")
            self.profile_layout.addWidget(lbl)
            return

        p = response.get("profile", {})

        # Username
        username_lbl = QLabel(p.get("username", "User"))
        username_lbl.setStyleSheet(
            "font-size: 22px; font-weight: 800; color: #60a5fa; background: transparent;"
        )
        self.profile_layout.addWidget(username_lbl)

        email_lbl = QLabel(p.get("email", ""))
        email_lbl.setStyleSheet("color: #475569; font-size: 12px; background: transparent;")
        self.profile_layout.addWidget(email_lbl)

        # Divider
        div = QFrame()
        div.setFixedHeight(1)
        div.setStyleSheet("background-color: rgba(51, 65, 85, 0.2); border: none;")
        self.profile_layout.addWidget(div)

        # Stats
        stats = [
            ("Total Sessions", str(p.get("total_sessions", 0))),
            ("Current Streak", f"{p.get('current_streak_days', 0)} days"),
            ("Avg Score", f"{p.get('total_score', 0.0):.1f}"),
        ]
        for label, val in stats:
            row = QHBoxLayout()
            lbl = QLabel(label)
            lbl.setStyleSheet("color: #475569; font-size: 13px; background: transparent;")
            row.addWidget(lbl)
            v = QLabel(val)
            v.setStyleSheet(
                "font-weight: 700; color: #e2e8f0; font-size: 13px; background: transparent;"
            )
            row.addStretch()
            row.addWidget(v)
            self.profile_layout.addLayout(row)

    def _build_achievements_tab(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        header = QLabel("ACHIEVEMENTS")
        header.setObjectName("SectionHeader")
        layout.addWidget(header)

        self.ach_layout = QVBoxLayout()
        self.ach_layout.setSpacing(10)
        layout.addLayout(self.ach_layout)
        layout.addStretch()

        scroll.setWidget(widget)
        return scroll

    # Maps server achievement IDs → (display name, description, icon emoji)
    ACHIEVEMENT_META = [
        ("first_session", "First Step",       "Complete your first focus session",    "🚀"),
        ("sessions_10",   "Dedicated",        "Complete 10 focus sessions",           "🔟"),
        ("sessions_50",   "Focused",          "Complete 50 focus sessions",           "💪"),
        ("sessions_100",  "Elite Focuser",    "Complete 100 focus sessions",          "👑"),
        ("focus_1h",      "One Hour Club",    "Accumulate 1 hour of total focus",     "⏰"),
        ("focus_10h",     "Ten Hour Warrior", "Accumulate 10 hours of total focus",   "⚔️"),
        ("focus_100h",    "Century Focuser",  "Accumulate 100 hours of total focus",  "💎"),
        ("streak_3",      "On a Roll",        "Maintain a 3-day focus streak",        "🔥"),
        ("streak_7",      "Week Warrior",     "Maintain a 7-day focus streak",        "⚡"),
        ("streak_30",     "Monthly Master",   "Maintain a 30-day focus streak",       "🏆"),
    ]

    def _load_achievements(self):
        for i in reversed(range(self.ach_layout.count())):
            w = self.ach_layout.itemAt(i).widget()
            if w: w.deleteLater()

        response = self.network_client.get_achievements()
        if response.get("status") != "success": return
        unlocked = {a["achievement_type"] for a in response.get("achievements", [])}

        for ach_type, name, desc, emoji in self.ACHIEVEMENT_META:
            card = QFrame()
            card.setObjectName("Card")
            cl = QHBoxLayout(card)
            cl.setContentsMargins(18, 14, 18, 14)
            cl.setSpacing(14)

            is_un = ach_type in unlocked

            # Icon circle with emoji
            icon = QLabel(emoji)
            icon_bg = "rgba(59, 130, 246, 0.1)" if is_un else "rgba(13, 18, 36, 0.8)"
            icon_border = "rgba(59, 130, 246, 0.3)" if is_un else "rgba(51, 65, 85, 0.3)"
            icon.setStyleSheet(
                f"font-size: 18px; "
                f"background: {icon_bg}; "
                f"border: 1px solid {icon_border}; "
                f"border-radius: 20px; "
                f"min-width: 40px; min-height: 40px; max-width: 40px; max-height: 40px;"
            )
            icon.setAlignment(Qt.AlignCenter)

            # Glow for unlocked
            if is_un:
                glow = QGraphicsDropShadowEffect()
                glow.setBlurRadius(20)
                glow.setColor(QColor(59, 130, 246, 40))
                glow.setOffset(0, 0)
                icon.setGraphicsEffect(glow)

            cl.addWidget(icon)

            tl = QVBoxLayout()
            tl.setSpacing(2)
            nl = QLabel(name)
            nl.setStyleSheet(
                f"font-weight: 700; font-size: 14px; "
                f"color: {'#f8fafc' if is_un else '#334155'}; background: transparent;"
            )
            tl.addWidget(nl)

            dl = QLabel(desc)
            dl.setStyleSheet(
                f"color: {'#64748b' if is_un else '#1e293b'}; "
                f"font-size: 12px; background: transparent;"
            )
            tl.addWidget(dl)
            cl.addLayout(tl)
            cl.addStretch()
            self.ach_layout.addWidget(card)

    def showEvent(self, event):
        super().showEvent(event)
        self._load_profile()
        self._load_achievements()