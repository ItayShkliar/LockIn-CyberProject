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
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)

        title = QLabel("Settings")
        title.setObjectName("Title")
        layout.addWidget(title)

        self.sub_tabs = QTabWidget()
        self.sub_tabs.addTab(self._build_blocked_apps_tab(), "Blocked Apps")
        self.sub_tabs.addTab(self._build_connection_tab(), "Connection")
        self.sub_tabs.addTab(self._build_profile_tab(), "My Profile")
        self.sub_tabs.addTab(self._build_achievements_tab(), "Achievements")

        layout.addWidget(self.sub_tabs)

    def _build_blocked_apps_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        info = QLabel("Added apps will count as distractions during focus sessions.")
        info.setObjectName("Subtitle")
        layout.addWidget(info)

        input_row = QHBoxLayout()
        self.app_input = QLineEdit()
        self.app_input.setPlaceholderText("e.g. chrome.exe")
        self.app_input.returnPressed.connect(self._add_blocked_app)
        input_row.addWidget(self.app_input)

        add_btn = QPushButton("Add")
        add_btn.setProperty("theme", "success")
        add_btn.setFixedWidth(80)
        add_btn.clicked.connect(self._add_blocked_app)
        input_row.addWidget(add_btn)
        layout.addLayout(input_row)

        self.blocked_list = QListWidget()
        layout.addWidget(self.blocked_list)

        remove_btn = QPushButton("Remove Selected")
        remove_btn.setProperty("theme", "danger")
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
        if not app_name: return
        config = self._read_config()
        blocked = config.get("blocked_apps", [])
        if app_name not in blocked:
            blocked.append(app_name)
            config["blocked_apps"] = blocked
            self._write_config(config)
        self.app_input.clear()
        self._load_blocked_apps()

    def _remove_blocked_app(self):
        selected = self.blocked_list.selectedItems()
        if not selected: return
        config = self._read_config()
        blocked = config.get("blocked_apps", [])
        for item in selected:
            app_name = item.text()
            if app_name in blocked: blocked.remove(app_name)
        config["blocked_apps"] = blocked
        self._write_config(config)
        self._load_blocked_apps()

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
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        layout.addWidget(QLabel("Server Host:"))
        self.host_input = QLineEdit()
        layout.addWidget(self.host_input)

        layout.addWidget(QLabel("Server Port:"))
        self.port_input = QSpinBox()
        self.port_input.setRange(1, 65535)
        layout.addWidget(self.port_input)

        config = self._read_config()
        self.host_input.setText(config.get("server_host", "127.0.0.1"))
        self.port_input.setValue(config.get("server_port", 65432))

        save_btn = QPushButton("Save Settings")
        save_btn.setProperty("theme", "primary")
        save_btn.clicked.connect(self._save_connection)
        layout.addWidget(save_btn)

        self.conn_status_lbl = QLabel("")
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
        layout.setContentsMargins(20, 20, 20, 20)

        self.profile_card = QFrame()
        self.profile_card.setObjectName("Card")
        self.profile_layout = QVBoxLayout(self.profile_card)
        layout.addWidget(self.profile_card)
        layout.addStretch()
        return widget

    def _load_profile(self):
        for i in reversed(range(self.profile_layout.count())):
            w = self.profile_layout.itemAt(i).widget()
            if w: w.deleteLater()

        if not self.network_client or not self.network_client.logged_in_user_id:
            self.profile_layout.addWidget(QLabel("Not logged in."))
            return

        response = self.network_client.get_user_profile()
        if response.get("status") != "success":
            self.profile_layout.addWidget(QLabel("Failed to load profile."))
            return

        p = response.get("profile", {})
        title = QLabel(p.get("username", "User"))
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #3b82f6;")
        self.profile_layout.addWidget(title)
        self.profile_layout.addWidget(QLabel(p.get("email", "")))
        
        self.profile_layout.addSpacing(20)
        
        stats = [
            ("Total Sessions", str(p.get("total_sessions", 0))),
            ("Current Streak", f"{p.get('current_streak_days', 0)} days"),
            ("Avg Score", f"{p.get('total_score', 0.0):.1f}")
        ]
        for label, val in stats:
            row = QHBoxLayout()
            row.addWidget(QLabel(label))
            v = QLabel(val)
            v.setStyleSheet("font-weight: bold;")
            row.addStretch()
            row.addWidget(v)
            self.profile_layout.addLayout(row)

    def _build_achievements_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        self.ach_layout = QVBoxLayout()
        self.ach_layout.setSpacing(10)
        layout.addLayout(self.ach_layout)
        layout.addStretch()
        return widget

    ACHIEVEMENT_META = {
        "first_session":  ("First Step", "Complete your first session"),
        "sessions_10":    ("Dedicated", "Complete 10 sessions"),
        "focus_1h":       ("One Hour Club", "Accumulate 1 hour focus"),
        "streak_3":       ("On a Roll", "Maintain a 3-day streak"),
    }

    def _load_achievements(self):
        for i in reversed(range(self.ach_layout.count())):
            w = self.ach_layout.itemAt(i).widget()
            if w: w.deleteLater()

        response = self.network_client.get_achievements()
        if response.get("status") != "success": return
        unlocked = {a["achievement_type"] for a in response.get("achievements", [])}

        for ach_type, (name, desc) in self.ACHIEVEMENT_META.items():
            card = QFrame()
            card.setObjectName("Card")
            cl = QHBoxLayout(card)
            
            is_un = ach_type in unlocked
            icon = QLabel("★" if is_un else "☆")
            icon.setStyleSheet(f"font-size: 24px; color: {'#10b981' if is_un else '#475569'};")
            cl.addWidget(icon)
            
            tl = QVBoxLayout()
            nl = QLabel(name)
            nl.setStyleSheet(f"font-weight: bold; color: {'#f8fafc' if is_un else '#475569'};")
            tl.addWidget(nl)
            tl.addWidget(QLabel(desc))
            cl.addLayout(tl)
            cl.addStretch()
            self.ach_layout.addWidget(card)

    def showEvent(self, event):
        super().showEvent(event)
        self._load_profile()
        self._load_achievements()