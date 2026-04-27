from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea, QFrame, QHBoxLayout
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
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(30)

        # Title
        self.greeting_label = QLabel("Hello, User")
        self.greeting_label.setObjectName("Title")
        main_layout.addWidget(self.greeting_label)

        # Dashboard Grid (using layouts inside cards)
        stats_container = QHBoxLayout()
        stats_container.setSpacing(20)

        # Today's Focus Card
        focus_card = QFrame()
        focus_card.setObjectName("Card")
        focus_layout = QVBoxLayout(focus_card)
        focus_layout.addWidget(QLabel("TODAY'S FOCUS"))
        self.daily_focus_label = QLabel("00:00:00")
        self.daily_focus_label.setStyleSheet("font-size: 28px; font-weight: bold; color: #3b82f6;")
        focus_layout.addWidget(self.daily_focus_label)
        stats_container.addWidget(focus_card)

        # Sessions Card
        session_card = QFrame()
        session_card.setObjectName("Card")
        session_layout = QVBoxLayout(session_card)
        session_layout.addWidget(QLabel("SESSIONS TODAY"))
        self.session_time_label = QLabel("0")
        self.session_time_label.setStyleSheet("font-size: 28px; font-weight: bold; color: #10b981;")
        session_layout.addWidget(self.session_time_label)
        stats_container.addWidget(session_card)

        main_layout.addLayout(stats_container)

        # Competition Card
        comp_card = QFrame()
        comp_card.setObjectName("Card")
        comp_layout = QVBoxLayout(comp_card)
        label = QLabel("ACTIVE COMPETITION")
        label.setObjectName("Subtitle")
        comp_layout.addWidget(label)
        
        self.comp_rank_label = QLabel("No active competitions")
        self.comp_rank_label.setStyleSheet("font-size: 20px; font-weight: 500; color: #f8fafc;")
        comp_layout.addWidget(self.comp_rank_label)
        main_layout.addWidget(comp_card)

        main_layout.addStretch()

    def refresh_data(self):
        if not self.network_client or not self.network_client.logged_in_user_id:
            return

        username = self.network_client.logged_in_username or "User"
        self.greeting_label.setText(f"Hello, {username}")

        try:
            daily_response = self.network_client.get_daily_stats()
            if daily_response.get("status") == "success":
                focus_formatted = daily_response.get("daily_focus_formatted", "00:00:00")
                sessions = daily_response.get("daily_sessions", 0)
                self.daily_focus_label.setText(focus_formatted)
                self.session_time_label.setText(str(sessions))
        except Exception as e:
            print(f"[HomeTab] Error fetching daily stats: {e}")

        try:
            comp_response = self.network_client.get_active_competition_leaderboard(limit=1)
            if comp_response.get("status") == "success":
                competition = comp_response.get("competition")
                leaderboard = comp_response.get("leaderboard", [])

                if competition and leaderboard:
                    comp_name = competition.get("name", "Unknown")
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
        super().showEvent(event)
        self.refresh_data()
