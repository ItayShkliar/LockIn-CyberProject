"""
Home Tab (v3) - Minimalistic Dashboard
Shows greeting, daily focus/session time, and current competition rank.
"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea
from PyQt5.QtCore import Qt, QTimer


class HomeTab(QWidget):
    def __init__(self, network_client=None):
        super().__init__()
        self.network_client = network_client
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_data)
        self._init_ui()
        self.refresh_timer.start(30000)

    def _init_ui(self):
        """Initialize the minimalistic scrollable UI."""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(20)

        # Scrollable content area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: #36393F; }")
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        scroll_layout.setSpacing(30)

        # Greeting
        self.greeting_label = QLabel("Hello, User")
        self.greeting_label.setStyleSheet("font-size: 32px; font-weight: bold; color: white;")
        scroll_layout.addWidget(self.greeting_label)

        # Daily Focus Time
        self.daily_focus_label = QLabel("Today's Focus: 00:00:00")
        self.daily_focus_label.setStyleSheet("font-size: 20px; color: #43B581;")
        scroll_layout.addWidget(self.daily_focus_label)

        # Overall Session Time
        self.session_time_label = QLabel("Sessions Today: 0")
        self.session_time_label.setStyleSheet("font-size: 18px; color: #B9BBBE;")
        scroll_layout.addWidget(self.session_time_label)

        # Competition Rank (if in any)
        self.comp_rank_label = QLabel("No active competitions")
        self.comp_rank_label.setStyleSheet("font-size: 16px; color: #FAA61A; margin-top: 20px;")
        scroll_layout.addWidget(self.comp_rank_label)

        scroll_layout.addStretch()
        scroll.setWidget(scroll_widget)
        main_layout.addWidget(scroll)

        self.setLayout(main_layout)

    def refresh_data(self):
        """Refresh daily stats and competition rank."""
        if not self.network_client or not self.network_client.logged_in_user_id:
            return

        # Update greeting
        username = self.network_client.logged_in_username or "User"
        self.greeting_label.setText(f"Hello, {username}")

        # Fetch daily stats
        try:
            daily_response = self.network_client.get_daily_stats()
            if daily_response.get("status") == "success":
                focus_formatted = daily_response.get("daily_focus_formatted", "00:00:00")
                sessions = daily_response.get("daily_sessions", 0)
                self.daily_focus_label.setText(f"Today's Focus: {focus_formatted}")
                self.session_time_label.setText(f"Sessions Today: {sessions}")
        except Exception as e:
            print(f"[HomeTab] Error fetching daily stats: {e}")

        # Fetch active competition rank
        try:
            comp_response = self.network_client.get_active_competition_leaderboard(limit=1)
            if comp_response.get("status") == "success":
                competition = comp_response.get("competition")
                leaderboard = comp_response.get("leaderboard", [])

                if competition and leaderboard:
                    comp_name = competition.get("name", "Unknown")
                    # Find user's rank in the leaderboard
                    user_rank = None
                    for entry in leaderboard:
                        if entry.get("username") == username:
                            user_rank = entry.get("rank")
                            break
                    if user_rank:
                        self.comp_rank_label.setText(f"{comp_name} - Rank #{user_rank}")
                    else:
                        self.comp_rank_label.setText(comp_name)
                else:
                    self.comp_rank_label.setText("No active competitions")
        except Exception as e:
            print(f"[HomeTab] Error fetching competition rank: {e}")

    def showEvent(self, event):
        """Called when the tab becomes visible."""
        super().showEvent(event)
        self.refresh_data()
