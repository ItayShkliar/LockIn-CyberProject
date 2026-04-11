"""
Settings Tab (v2)
Allows users to manage blocked apps, server connection settings,
and view their profile/achievements.
"""
import json
import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QListWidget, QListWidgetItem, QMessageBox,
    QTabWidget, QFrame, QSpinBox
)
from PyQt5.QtCore import Qt


CONFIG_FILE = "lockin_config.json"


class SettingsTab(QWidget):
    def __init__(self, network_client=None):
        super().__init__()
        self.network_client = network_client
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)

        title = QLabel("Settings")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: white;")
        layout.addWidget(title)

        self.sub_tabs = QTabWidget()
        self.sub_tabs.setStyleSheet("""
            QTabWidget::pane { border: 1px solid #2F3136; background: #2F3136; border-radius: 8px; }
            QTabBar::tab { background: #202225; color: #B9BBBE; padding: 8px 20px; border-radius: 4px; }
            QTabBar::tab:selected { background: #7289DA; color: white; font-weight: bold; }
        """)

        self.sub_tabs.addTab(self._build_blocked_apps_tab(), "Blocked Apps")
        self.sub_tabs.addTab(self._build_connection_tab(), "Connection")
        self.sub_tabs.addTab(self._build_profile_tab(), "My Profile")
        self.sub_tabs.addTab(self._build_achievements_tab(), "Achievements")

        layout.addWidget(self.sub_tabs)
        self.setLayout(layout)

    # -----------------------------------------------------------------------
    # Blocked Apps tab
    # -----------------------------------------------------------------------

    def _build_blocked_apps_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        info = QLabel(
            "Apps listed here will be treated as distractions during focus sessions.\n"
            "Enter the process name (e.g. chrome.exe, discord.exe)."
        )
        info.setStyleSheet("color: #B9BBBE; font-size: 13px;")
        info.setWordWrap(True)
        layout.addWidget(info)

        input_row = QHBoxLayout()
        self.app_input = QLineEdit()
        self.app_input.setPlaceholderText("e.g. discord.exe")
        self.app_input.setStyleSheet(
            "background-color: #202225; color: white; border: 1px solid #4F545C; "
            "border-radius: 4px; padding: 8px;"
        )
        self.app_input.returnPressed.connect(self._add_blocked_app)
        input_row.addWidget(self.app_input)

        add_btn = QPushButton("Add")
        add_btn.setFixedWidth(80)
        add_btn.setStyleSheet("background-color: #43B581; color: white; border-radius: 4px; padding: 8px;")
        add_btn.clicked.connect(self._add_blocked_app)
        input_row.addWidget(add_btn)
        layout.addLayout(input_row)

        list_lbl = QLabel("Currently Blocked Apps:")
        list_lbl.setStyleSheet("color: white; font-weight: bold; font-size: 14px;")
        layout.addWidget(list_lbl)

        self.blocked_list = QListWidget()
        self.blocked_list.setStyleSheet("""
            QListWidget { background-color: #202225; color: white; border: 1px solid #4F545C; border-radius: 4px; }
            QListWidget::item { padding: 6px; }
            QListWidget::item:selected { background-color: #7289DA; }
        """)
        layout.addWidget(self.blocked_list)

        remove_btn = QPushButton("Remove Selected")
        remove_btn.setStyleSheet("background-color: #E74C3C; color: white; border-radius: 4px; padding: 8px;")
        remove_btn.clicked.connect(self._remove_blocked_app)
        layout.addWidget(remove_btn, alignment=Qt.AlignRight)

        self._load_blocked_apps()
        return widget

    def _load_blocked_apps(self):
        self.blocked_list.clear()
        config = self._read_config()
        for app in config.get("blocked_apps", []):
            self.blocked_list.addItem(QListWidgetItem(app))

    def _add_blocked_app(self):
        app_name = self.app_input.text().strip().lower()
        if not app_name:
            return
        config = self._read_config()
        blocked = config.get("blocked_apps", [])
        if app_name in blocked:
            QMessageBox.information(self, "Already Added", f"'{app_name}' is already in the list.")
            return
        blocked.append(app_name)
        config["blocked_apps"] = blocked
        self._write_config(config)
        self.app_input.clear()
        self._load_blocked_apps()

    def _remove_blocked_app(self):
        selected = self.blocked_list.selectedItems()
        if not selected:
            QMessageBox.information(self, "No Selection", "Please select an app to remove.")
            return
        config = self._read_config()
        blocked = config.get("blocked_apps", [])
        for item in selected:
            app_name = item.text()
            if app_name in blocked:
                blocked.remove(app_name)
        config["blocked_apps"] = blocked
        self._write_config(config)
        self._load_blocked_apps()

    def _read_config(self) -> dict:
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f:
                    return json.load(f)
            except Exception:
                pass
        return {"blocked_apps": []}

    def _write_config(self, config: dict):
        try:
            with open(CONFIG_FILE, "w") as f:
                json.dump(config, f, indent=4)
        except Exception as e:
            QMessageBox.warning(self, "Save Error", f"Could not save settings: {e}")

    # -----------------------------------------------------------------------
    # Connection tab
    # -----------------------------------------------------------------------

    def _build_connection_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        info = QLabel("Configure the server connection. Restart the app after changing.")
        info.setStyleSheet("color: #B9BBBE; font-size: 13px;")
        layout.addWidget(info)

        host_lbl = QLabel("Server Host:")
        host_lbl.setStyleSheet("color: white; font-size: 13px;")
        layout.addWidget(host_lbl)

        self.host_input = QLineEdit()
        self.host_input.setPlaceholderText("127.0.0.1")
        self.host_input.setStyleSheet(
            "background-color: #202225; color: white; border: 1px solid #4F545C; "
            "border-radius: 4px; padding: 8px;"
        )
        layout.addWidget(self.host_input)

        port_lbl = QLabel("Server Port:")
        port_lbl.setStyleSheet("color: white; font-size: 13px;")
        layout.addWidget(port_lbl)

        self.port_input = QSpinBox()
        self.port_input.setRange(1024, 65535)
        self.port_input.setValue(65432)
        self.port_input.setStyleSheet(
            "background-color: #202225; color: white; border: 1px solid #4F545C; "
            "border-radius: 4px; padding: 6px;"
        )
        layout.addWidget(self.port_input)

        config = self._read_config()
        self.host_input.setText(config.get("server_host", "127.0.0.1"))
        self.port_input.setValue(config.get("server_port", 65432))

        save_btn = QPushButton("Save Connection Settings")
        save_btn.setStyleSheet("background-color: #7289DA; color: white; border-radius: 4px; padding: 10px;")
        save_btn.clicked.connect(self._save_connection)
        layout.addWidget(save_btn)

        test_btn = QPushButton("Test Connection")
        test_btn.setStyleSheet("background-color: #43B581; color: white; border-radius: 4px; padding: 10px;")
        test_btn.clicked.connect(self._test_connection)
        layout.addWidget(test_btn)

        self.conn_status_lbl = QLabel("")
        self.conn_status_lbl.setStyleSheet("font-size: 13px; padding: 5px;")
        layout.addWidget(self.conn_status_lbl)

        layout.addStretch()
        return widget

    def _save_connection(self):
        config = self._read_config()
        config["server_host"] = self.host_input.text().strip() or "127.0.0.1"
        config["server_port"] = self.port_input.value()
        self._write_config(config)
        QMessageBox.information(self, "Saved", "Connection settings saved. Restart the app to apply.")

    def _test_connection(self):
        if not self.network_client:
            self.conn_status_lbl.setText("No network client available.")
            self.conn_status_lbl.setStyleSheet("color: #E74C3C; font-size: 13px;")
            return
        try:
            import socket
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(3)
            s.connect((self.network_client.host, self.network_client.port))
            s.close()
            self.conn_status_lbl.setText(
                f"Connected to {self.network_client.host}:{self.network_client.port}"
            )
            self.conn_status_lbl.setStyleSheet("color: #43B581; font-size: 13px;")
        except Exception as e:
            self.conn_status_lbl.setText(f"Connection failed: {e}")
            self.conn_status_lbl.setStyleSheet("color: #E74C3C; font-size: 13px;")

    # -----------------------------------------------------------------------
    # Profile tab
    # -----------------------------------------------------------------------

    def _build_profile_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        refresh_btn = QPushButton("Refresh Profile")
        refresh_btn.setFixedWidth(150)
        refresh_btn.setStyleSheet("background-color: #7289DA; color: white; border-radius: 4px; padding: 6px;")
        refresh_btn.clicked.connect(self._load_profile)
        layout.addWidget(refresh_btn, alignment=Qt.AlignRight)

        self.profile_frame = QFrame()
        self.profile_frame.setStyleSheet("background-color: #202225; border-radius: 8px; padding: 15px;")
        self.profile_layout = QVBoxLayout(self.profile_frame)
        layout.addWidget(self.profile_frame)

        layout.addStretch()
        return widget

    def _load_profile(self):
        for i in reversed(range(self.profile_layout.count())):
            w = self.profile_layout.itemAt(i).widget()
            if w:
                w.deleteLater()

        if not self.network_client or not self.network_client.logged_in_user_id:
            lbl = QLabel("Not logged in.")
            lbl.setStyleSheet("color: #B9BBBE;")
            self.profile_layout.addWidget(lbl)
            return

        response = self.network_client.get_user_profile()
        if response.get("status") != "success":
            lbl = QLabel(f"Error: {response.get('message', 'Failed to load profile')}")
            lbl.setStyleSheet("color: #E74C3C;")
            self.profile_layout.addWidget(lbl)
            return

        profile = response.get("profile", {})

        def stat_row(label: str, value: str):
            row = QHBoxLayout()
            lbl = QLabel(label)
            lbl.setStyleSheet("color: #B9BBBE; font-size: 13px; min-width: 200px;")
            val = QLabel(value)
            val.setStyleSheet("color: white; font-size: 13px; font-weight: bold;")
            row.addWidget(lbl)
            row.addWidget(val)
            row.addStretch()
            return row

        username_lbl = QLabel(profile.get("username", "Unknown"))
        username_lbl.setStyleSheet("color: #7289DA; font-size: 22px; font-weight: bold;")
        self.profile_layout.addWidget(username_lbl)

        email_lbl = QLabel(profile.get("email", ""))
        email_lbl.setStyleSheet("color: #B9BBBE; font-size: 13px;")
        self.profile_layout.addWidget(email_lbl)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("color: #4F545C;")
        self.profile_layout.addWidget(sep)

        total_focus = profile.get("total_focus_time_seconds", 0)
        h = total_focus // 3600
        m = (total_focus % 3600) // 60
        focus_str = f"{h}h {m}m"

        best = profile.get("best_session_seconds", 0)
        bh = best // 3600
        bm = (best % 3600) // 60
        best_str = f"{bh}h {bm}m"

        stats = [
            ("Total Sessions:", str(profile.get("total_sessions", 0))),
            ("Total Focus Time:", focus_str),
            ("Best Session:", best_str),
            ("Current Streak:", f"{profile.get('current_streak_days', 0)} days"),
            ("Longest Streak:", f"{profile.get('longest_streak_days', 0)} days"),
            ("Avg Focus Score:", f"{profile.get('total_score', 0.0):.1f} / 100"),
            ("Total Distractions:", str(profile.get("total_distractions", 0))),
        ]
        for label, value in stats:
            self.profile_layout.addLayout(stat_row(label, value))

    # -----------------------------------------------------------------------
    # Achievements tab
    # -----------------------------------------------------------------------

    def _build_achievements_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)

        refresh_btn = QPushButton("Refresh Achievements")
        refresh_btn.setFixedWidth(180)
        refresh_btn.setStyleSheet("background-color: #7289DA; color: white; border-radius: 4px; padding: 6px;")
        refresh_btn.clicked.connect(self._load_achievements)
        layout.addWidget(refresh_btn, alignment=Qt.AlignRight)

        self.ach_container = QWidget()
        self.ach_layout = QVBoxLayout(self.ach_container)
        self.ach_layout.setAlignment(Qt.AlignTop)
        self.ach_layout.setSpacing(8)
        layout.addWidget(self.ach_container)
        layout.addStretch()
        return widget

    ACHIEVEMENT_META = {
        "first_session":  ("First Step",         "Complete your first focus session",          "#43B581"),
        "sessions_10":    ("Dedicated",           "Complete 10 focus sessions",                 "#7289DA"),
        "sessions_50":    ("Focused",             "Complete 50 focus sessions",                 "#FAA61A"),
        "sessions_100":   ("Elite Focuser",       "Complete 100 focus sessions",                "#E74C3C"),
        "focus_1h":       ("One Hour Club",       "Accumulate 1 hour of focus time",            "#43B581"),
        "focus_10h":      ("Ten Hour Warrior",    "Accumulate 10 hours of focus time",          "#7289DA"),
        "focus_100h":     ("Century Focuser",     "Accumulate 100 hours of focus time",         "#FAA61A"),
        "streak_3":       ("On a Roll",           "Maintain a 3-day focus streak",              "#43B581"),
        "streak_7":       ("Week Warrior",        "Maintain a 7-day focus streak",              "#7289DA"),
        "streak_30":      ("Monthly Master",      "Maintain a 30-day focus streak",             "#E74C3C"),
    }

    def _load_achievements(self):
        for i in reversed(range(self.ach_layout.count())):
            w = self.ach_layout.itemAt(i).widget()
            if w:
                w.deleteLater()

        if not self.network_client or not self.network_client.logged_in_user_id:
            lbl = QLabel("Not logged in.")
            lbl.setStyleSheet("color: #B9BBBE;")
            self.ach_layout.addWidget(lbl)
            return

        response = self.network_client.get_achievements()
        if response.get("status") != "success":
            lbl = QLabel(f"Error: {response.get('message', 'Failed')}")
            lbl.setStyleSheet("color: #E74C3C;")
            self.ach_layout.addWidget(lbl)
            return

        unlocked = {a["achievement_type"]: a for a in response.get("achievements", [])}

        for ach_type, (name, desc, color) in self.ACHIEVEMENT_META.items():
            card = QFrame()
            is_unlocked = ach_type in unlocked
            bg = "#202225" if is_unlocked else "#18191c"
            card.setStyleSheet(f"QFrame {{ background-color: {bg}; border-radius: 6px; padding: 10px; }}")
            card_layout = QHBoxLayout(card)

            icon_lbl = QLabel("★" if is_unlocked else "☆")
            icon_lbl.setStyleSheet(
                f"font-size: 20px; min-width: 30px; color: {color if is_unlocked else '#4F545C'};"
            )
            card_layout.addWidget(icon_lbl)

            text_col = QVBoxLayout()
            name_lbl = QLabel(name)
            name_lbl.setStyleSheet(
                f"color: {color if is_unlocked else '#4F545C'}; font-weight: bold; font-size: 14px;"
            )
            text_col.addWidget(name_lbl)
            desc_lbl = QLabel(desc)
            desc_lbl.setStyleSheet(
                f"color: {'#B9BBBE' if is_unlocked else '#4F545C'}; font-size: 12px;"
            )
            text_col.addWidget(desc_lbl)
            card_layout.addLayout(text_col)
            card_layout.addStretch()

            if is_unlocked:
                date_str = unlocked[ach_type].get("unlocked_at", "")[:10]
                date_lbl = QLabel(f"Unlocked {date_str}")
                date_lbl.setStyleSheet("color: #43B581; font-size: 11px;")
                card_layout.addWidget(date_lbl)
            else:
                locked_lbl = QLabel("Locked")
                locked_lbl.setStyleSheet("color: #4F545C; font-size: 11px;")
                card_layout.addWidget(locked_lbl)

            self.ach_layout.addWidget(card)

    def showEvent(self, event):
        super().showEvent(event)
        self._load_profile()
        self._load_achievements()