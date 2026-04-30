"""
Leaderboard Tab — Global rankings and competition lookup.
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QTabWidget,
    QLineEdit, QFrame
)
from PyQt5.QtCore import Qt

class LeaderboardTab(QWidget):
    def __init__(self, network_client):
        super().__init__()
        self.network_client = network_client
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(44, 44, 44, 44)
        layout.setSpacing(24)

        title = QLabel("Leaderboards")
        title.setObjectName("Title")
        layout.addWidget(title)

        subtitle = QLabel("See where you stand among the best focusers.")
        subtitle.setStyleSheet("color: #475569; font-size: 13px; margin-bottom: 4px;")
        layout.addWidget(subtitle)

        self.sub_tabs = QTabWidget()
        self.sub_tabs.addTab(self._build_global_tab(), "Global Top 20")
        self.sub_tabs.addTab(self._build_competition_tab(), "Competition Lookup")

        layout.addWidget(self.sub_tabs)

    def _build_global_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 24, 20, 20)
        layout.setSpacing(16)

        header = QHBoxLayout()
        title = QLabel("TOP 20 GLOBAL FOCUSERS")
        title.setObjectName("SectionHeader")
        header.addWidget(title)
        header.addStretch()

        refresh_btn = QPushButton("↻  Refresh")
        refresh_btn.setProperty("theme", "primary")
        refresh_btn.setFixedWidth(110)
        refresh_btn.setFixedHeight(34)
        refresh_btn.setCursor(Qt.PointingHandCursor)
        refresh_btn.clicked.connect(self._load_global_leaderboard)
        header.addWidget(refresh_btn)
        layout.addLayout(header)

        self.global_table = QTableWidget()
        self.global_table.setColumnCount(6)
        self.global_table.setHorizontalHeaderLabels(
            ["Rank", "User", "Total Focus", "Sessions", "Best", "Streak"]
        )
        self.global_table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.global_table.horizontalHeader().setStretchLastSection(True)
        self.global_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.global_table.verticalHeader().setDefaultSectionSize(42)
        layout.addWidget(self.global_table)
        return widget

    def _load_global_leaderboard(self):
        response = self.network_client.get_global_leaderboard(limit=20)
        if response.get("status") != "success": return

        leaderboard = response.get("leaderboard", [])
        self.global_table.setRowCount(len(leaderboard))
        for i, entry in enumerate(leaderboard):
            rank = entry.get("rank", i + 1)
            self.global_table.setItem(i, 0, QTableWidgetItem(f"#{rank}"))
            self.global_table.setItem(i, 1, QTableWidgetItem(entry.get("username", "")))
            self.global_table.setItem(i, 2, QTableWidgetItem(entry.get("focus_time_formatted", "00:00:00")))
            self.global_table.setItem(i, 3, QTableWidgetItem(str(entry.get("total_sessions", 0))))
            self.global_table.setItem(i, 4, QTableWidgetItem(entry.get("best_session_formatted", "00:00:00")))
            streak = entry.get("current_streak_days", 0)
            self.global_table.setItem(i, 5, QTableWidgetItem(f"{streak}d 🔥"))

    def _build_competition_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 24, 20, 20)
        layout.setSpacing(16)

        header = QLabel("COMPETITION LOOKUP")
        header.setObjectName("SectionHeader")
        layout.addWidget(header)

        search_row = QHBoxLayout()
        search_row.setSpacing(10)
        self.comp_code_input = QLineEdit()
        self.comp_code_input.setPlaceholderText("Enter room code...")
        self.comp_code_input.setFixedHeight(40)
        search_row.addWidget(self.comp_code_input)

        lookup_btn = QPushButton("Load")
        lookup_btn.setProperty("theme", "primary")
        lookup_btn.setFixedHeight(40)
        lookup_btn.setFixedWidth(80)
        lookup_btn.setCursor(Qt.PointingHandCursor)
        lookup_btn.clicked.connect(self._load_competition_leaderboard)
        search_row.addWidget(lookup_btn)
        layout.addLayout(search_row)

        self.comp_title_lbl = QLabel("Enter a code above to view rankings")
        self.comp_title_lbl.setStyleSheet("color: #334155; font-size: 13px;")
        layout.addWidget(self.comp_title_lbl)

        self.comp_table = QTableWidget()
        self.comp_table.setColumnCount(5)
        self.comp_table.setHorizontalHeaderLabels(["Rank", "User", "Focus Time", "Sessions", "Score"])
        self.comp_table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.comp_table.horizontalHeader().setStretchLastSection(True)
        self.comp_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.comp_table.verticalHeader().setDefaultSectionSize(42)
        layout.addWidget(self.comp_table)
        return widget

    def _load_competition_leaderboard(self):
        code_text = self.comp_code_input.text().strip()
        if not code_text: return
        try:
            code = int(code_text)
        except ValueError: return

        response = self.network_client.get_leaderboard(code)
        if response.get("status") != "success":
            self.comp_title_lbl.setText(f"Error: {response.get('message', 'Failed')}")
            self.comp_title_lbl.setStyleSheet("color: #f87171; font-size: 13px;")
            return

        leaderboard = response.get("leaderboard", [])
        self.comp_title_lbl.setText(f"Competition #{code} — {len(leaderboard)} participant(s)")
        self.comp_title_lbl.setStyleSheet("color: #60a5fa; font-size: 13px; font-weight: 600;")
        self.comp_table.setRowCount(len(leaderboard))

        for i, entry in enumerate(leaderboard):
            rank = entry.get("rank", i + 1)
            self.comp_table.setItem(i, 0, QTableWidgetItem(f"#{rank}"))
            self.comp_table.setItem(i, 1, QTableWidgetItem(entry.get("username", "")))
            self.comp_table.setItem(i, 2, QTableWidgetItem(entry.get("focus_time_formatted", "00:00:00")))
            table_sessions = str(entry.get("sessions_count", 0))
            self.comp_table.setItem(i, 3, QTableWidgetItem(table_sessions))
            self.comp_table.setItem(i, 4, QTableWidgetItem(f"{entry.get('focus_score', 0):.1f}"))

    def showEvent(self, event):
        super().showEvent(event)
        self._load_global_leaderboard()
