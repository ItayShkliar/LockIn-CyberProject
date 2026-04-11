"""
Leaderboard Tab (v2)
Shows both the Global Leaderboard (all users) and Competition-specific leaderboards.
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
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)

        title = QLabel("Leaderboards")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: white;")
        layout.addWidget(title)

        self.sub_tabs = QTabWidget()
        self.sub_tabs.setStyleSheet("""
            QTabWidget::pane { border: 1px solid #2F3136; background: #2F3136; border-radius: 8px; }
            QTabBar::tab { background: #202225; color: #B9BBBE; padding: 8px 20px; border-radius: 4px; }
            QTabBar::tab:selected { background: #7289DA; color: white; font-weight: bold; }
        """)

        self.sub_tabs.addTab(self._build_global_tab(), "Global Top 20")
        self.sub_tabs.addTab(self._build_competition_tab(), "Competition Lookup")

        layout.addWidget(self.sub_tabs)
        self.setLayout(layout)

    # -----------------------------------------------------------------------
    # Global leaderboard tab
    # -----------------------------------------------------------------------

    def _build_global_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(15, 15, 15, 15)

        header = QHBoxLayout()
        subtitle = QLabel("Top 20 users by total focus time")
        subtitle.setStyleSheet("color: #B9BBBE; font-size: 13px;")
        header.addWidget(subtitle)
        header.addStretch()

        refresh_btn = QPushButton("Refresh")
        refresh_btn.setFixedWidth(100)
        refresh_btn.setStyleSheet("background-color: #7289DA; color: white; border-radius: 4px; padding: 6px;")
        refresh_btn.clicked.connect(self._load_global_leaderboard)
        header.addWidget(refresh_btn)
        layout.addLayout(header)

        self.global_table = QTableWidget()
        self.global_table.setColumnCount(6)
        self.global_table.setHorizontalHeaderLabels(
            ["Rank", "Username", "Total Focus", "Sessions", "Best Session", "Streak"]
        )
        self.global_table.setStyleSheet("""
            QTableWidget { background-color: #202225; color: white; border: none; border-radius: 5px; gridline-color: #2F3136; }
            QHeaderView::section { background-color: #2F3136; color: white; font-weight: bold; border: none; padding: 8px; }
            QTableWidget::item { padding: 6px; }
            QTableWidget::item:selected { background-color: #7289DA; }
        """)
        self.global_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.global_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.global_table.setAlternatingRowColors(True)
        layout.addWidget(self.global_table)
        return widget

    def _load_global_leaderboard(self):
        response = self.network_client.get_global_leaderboard(limit=20)
        if response.get("status") != "success":
            return

        leaderboard = response.get("leaderboard", [])
        self.global_table.setRowCount(len(leaderboard))

        medal_map = {1: "🥇 #1", 2: "🥈 #2", 3: "🥉 #3"}

        for i, entry in enumerate(leaderboard):
            rank = entry.get("rank", i + 1)
            rank_str = medal_map.get(rank, f"#{rank}")

            self.global_table.setItem(i, 0, QTableWidgetItem(rank_str))
            self.global_table.setItem(i, 1, QTableWidgetItem(entry.get("username", "")))
            self.global_table.setItem(i, 2, QTableWidgetItem(entry.get("focus_time_formatted", "00:00:00")))
            self.global_table.setItem(i, 3, QTableWidgetItem(str(entry.get("total_sessions", 0))))
            self.global_table.setItem(i, 4, QTableWidgetItem(entry.get("best_session_formatted", "00:00:00")))
            streak = entry.get("current_streak_days", 0)
            streak_str = f"{streak} day{'s' if streak != 1 else ''}"
            self.global_table.setItem(i, 5, QTableWidgetItem(streak_str))

            # Highlight top 3
            if rank <= 3:
                colors = {1: "#FFD700", 2: "#C0C0C0", 3: "#CD7F32"}
                color = colors.get(rank, "white")
                for col in range(6):
                    item = self.global_table.item(i, col)
                    if item:
                        item.setForeground(Qt.white)

    # -----------------------------------------------------------------------
    # Competition lookup tab
    # -----------------------------------------------------------------------

    def _build_competition_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(15, 15, 15, 15)

        search_row = QHBoxLayout()
        self.comp_code_input = QLineEdit()
        self.comp_code_input.setPlaceholderText("Enter competition code (e.g. 42)")
        self.comp_code_input.setStyleSheet(
            "background-color: #202225; color: white; border: 1px solid #4F545C; "
            "border-radius: 4px; padding: 8px;"
        )
        search_row.addWidget(self.comp_code_input)

        lookup_btn = QPushButton("Load Leaderboard")
        lookup_btn.setStyleSheet("background-color: #7289DA; color: white; border-radius: 4px; padding: 8px 16px;")
        lookup_btn.clicked.connect(self._load_competition_leaderboard)
        search_row.addWidget(lookup_btn)
        layout.addLayout(search_row)

        self.comp_title_lbl = QLabel("Enter a competition code above to view its leaderboard")
        self.comp_title_lbl.setStyleSheet("color: #B9BBBE; font-size: 13px; padding: 5px;")
        layout.addWidget(self.comp_title_lbl)

        self.comp_table = QTableWidget()
        self.comp_table.setColumnCount(5)
        self.comp_table.setHorizontalHeaderLabels(["Rank", "Username", "Focus Time", "Sessions", "Score"])
        self.comp_table.setStyleSheet("""
            QTableWidget { background-color: #202225; color: white; border: none; border-radius: 5px; gridline-color: #2F3136; }
            QHeaderView::section { background-color: #2F3136; color: white; font-weight: bold; border: none; padding: 8px; }
            QTableWidget::item { padding: 6px; }
        """)
        self.comp_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.comp_table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.comp_table)
        return widget

    def _load_competition_leaderboard(self):
        code_text = self.comp_code_input.text().strip()
        if not code_text:
            return
        try:
            code = int(code_text)
        except ValueError:
            self.comp_title_lbl.setText("Invalid code — must be a number")
            return

        response = self.network_client.get_leaderboard(code)
        if response.get("status") != "success":
            self.comp_title_lbl.setText(f"Error: {response.get('message', 'Failed to load')}")
            return

        leaderboard = response.get("leaderboard", [])
        self.comp_title_lbl.setText(f"Competition #{code} — {len(leaderboard)} participant(s)")
        self.comp_table.setRowCount(len(leaderboard))

        medal_map = {1: "🥇 #1", 2: "🥈 #2", 3: "🥉 #3"}
        for i, entry in enumerate(leaderboard):
            rank = entry.get("rank", i + 1)
            self.comp_table.setItem(i, 0, QTableWidgetItem(medal_map.get(rank, f"#{rank}")))
            self.comp_table.setItem(i, 1, QTableWidgetItem(entry.get("username", "")))
            self.comp_table.setItem(i, 2, QTableWidgetItem(entry.get("focus_time_formatted", "00:00:00")))
            self.comp_table.setItem(i, 3, QTableWidgetItem(str(entry.get("sessions_count", 0))))
            self.comp_table.setItem(i, 4, QTableWidgetItem(f"{entry.get('focus_score', 0):.1f}"))

    # -----------------------------------------------------------------------
    # Qt lifecycle
    # -----------------------------------------------------------------------

    def showEvent(self, event):
        super().showEvent(event)
        self._load_global_leaderboard()
