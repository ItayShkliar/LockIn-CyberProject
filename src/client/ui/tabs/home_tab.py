from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QScrollArea,
                             QFrame, QHBoxLayout, QGridLayout)
from PyQt5.QtCore import Qt, QTimer
from datetime import datetime


class HomeTab(QWidget):
    def __init__(self, network_client=None):
        super().__init__()
        self.network_client = network_client
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_data)
        self._init_ui()
        self.refresh_timer.start(30000)

    def _time_greeting(self):
        hour = datetime.now().hour
        if hour < 12:
            return "Good Morning"
        elif hour < 17:
            return "Good Afternoon"
        elif hour < 21:
            return "Good Evening"
        else:
            return "Night Owl Mode"

    def _init_ui(self):
        # Outer scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        inner = QWidget()
        layout = QVBoxLayout(inner)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(24)

        # ---- Greeting ----
        self.greeting_label = QLabel("Hello, User")
        self.greeting_label.setObjectName("Title")
        layout.addWidget(self.greeting_label)

        self.subtitle_label = QLabel("Let's stay focused today.")
        self.subtitle_label.setStyleSheet("font-size: 14px; color: #94a3b8; margin-bottom: 8px;")
        layout.addWidget(self.subtitle_label)

        # ---- Stats Row (3 cards) ----
        stats_grid = QHBoxLayout()
        stats_grid.setSpacing(16)

        # Card 1: Today's Focus
        self.focus_card = self._make_stat_card(
            "TODAY'S FOCUS", "00:00:00", "#3b82f6", "focus_value"
        )
        stats_grid.addWidget(self.focus_card)

        # Card 2: Sessions Today
        self.sessions_card = self._make_stat_card(
            "SESSIONS TODAY", "0", "#10b981", "sessions_value"
        )
        stats_grid.addWidget(self.sessions_card)

        # Card 3: Avg Focus Ratio
        self.ratio_card = self._make_stat_card(
            "AVG FOCUS RATIO", "0%", "#a855f7", "ratio_value"
        )
        stats_grid.addWidget(self.ratio_card)

        layout.addLayout(stats_grid)

        # ---- Active Competitions Section ----
        comp_header = QLabel("ACTIVE COMPETITIONS")
        comp_header.setObjectName("Subtitle")
        comp_header.setStyleSheet("font-size: 13px; font-weight: bold; color: #94a3b8; letter-spacing: 1px; margin-top: 8px;")
        layout.addWidget(comp_header)

        self.comps_container = QVBoxLayout()
        self.comps_container.setSpacing(12)

        self.no_comps_label = QLabel("No active competitions. Join one from the Competitions tab!")
        self.no_comps_label.setStyleSheet("color: #64748b; font-size: 13px; padding: 20px 0;")
        self.comps_container.addWidget(self.no_comps_label)

        layout.addLayout(self.comps_container)
        layout.addStretch()

        scroll.setWidget(inner)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

    def _make_stat_card(self, title: str, value: str, color: str, obj_name: str) -> QFrame:
        card = QFrame()
        card.setObjectName("Card")
        card.setMinimumHeight(100)
        cl = QVBoxLayout(card)
        cl.setContentsMargins(20, 16, 20, 16)
        cl.setSpacing(6)

        lbl = QLabel(title)
        lbl.setStyleSheet("font-size: 11px; font-weight: bold; color: #94a3b8; letter-spacing: 1px;")
        cl.addWidget(lbl)

        val = QLabel(value)
        val.setObjectName(obj_name)
        val.setStyleSheet(f"font-size: 32px; font-weight: bold; color: {color};")
        cl.addWidget(val)

        return card

    def _make_comp_card(self, comp: dict) -> QFrame:
        card = QFrame()
        card.setObjectName("Card")
        card.setStyleSheet("""
            QFrame#Card {
                border-left: 3px solid #3b82f6;
            }
        """)
        cl = QHBoxLayout(card)
        cl.setContentsMargins(16, 12, 16, 12)
        cl.setSpacing(16)

        # Left: Info
        info_layout = QVBoxLayout()
        info_layout.setSpacing(4)

        name_lbl = QLabel(comp.get("name", "Competition"))
        name_lbl.setStyleSheet("font-size: 16px; font-weight: bold; color: #f8fafc;")
        info_layout.addWidget(name_lbl)

        focus_apps = comp.get("focus_apps")
        if focus_apps:
            apps_text = ", ".join(focus_apps)
            apps_lbl = QLabel(f"Focus: {apps_text}")
            apps_lbl.setStyleSheet("font-size: 11px; color: #38bdf8; font-weight: 500;")
            info_layout.addWidget(apps_lbl)
        else:
            gen_lbl = QLabel("General Competition")
            gen_lbl.setStyleSheet("font-size: 11px; color: #94a3b8;")
            info_layout.addWidget(gen_lbl)

        time_lbl = QLabel(f"Your time: {comp.get('my_focus_time_formatted', '00:00:00')}")
        time_lbl.setStyleSheet("font-size: 12px; color: #94a3b8;")
        info_layout.addWidget(time_lbl)

        cl.addLayout(info_layout, stretch=1)

        # Right: Rank badge
        rank = comp.get("my_rank", "?")
        total = comp.get("total_participants", "?")
        rank_frame = QFrame()
        rank_layout = QVBoxLayout(rank_frame)
        rank_layout.setContentsMargins(12, 8, 12, 8)
        rank_layout.setSpacing(2)
        rank_layout.setAlignment(Qt.AlignCenter)

        rank_color = "#fbbf24" if rank == 1 else "#94a3b8" if rank == 2 else "#cd7f32" if rank == 3 else "#64748b"
        rank_num = QLabel(f"#{rank}" if rank else "?")
        rank_num.setStyleSheet(f"font-size: 28px; font-weight: bold; color: {rank_color};")
        rank_num.setAlignment(Qt.AlignCenter)
        rank_layout.addWidget(rank_num)

        of_lbl = QLabel(f"of {total}")
        of_lbl.setStyleSheet("font-size: 11px; color: #64748b;")
        of_lbl.setAlignment(Qt.AlignCenter)
        rank_layout.addWidget(of_lbl)

        cl.addWidget(rank_frame)

        return card

    def refresh_data(self):
        if not self.network_client or not self.network_client.logged_in_user_id:
            return

        username = self.network_client.logged_in_username or "User"
        greeting = self._time_greeting()
        self.greeting_label.setText(f"{greeting}, {username}")

        # Daily stats
        try:
            daily_response = self.network_client.get_daily_stats()
            if daily_response.get("status") == "success":
                focus_formatted = daily_response.get("daily_focus_formatted", "00:00:00")
                sessions = daily_response.get("daily_sessions", 0)
                ratio = daily_response.get("daily_avg_focus_ratio", 0)

                self.focus_card.findChild(QLabel, "focus_value").setText(focus_formatted)
                self.sessions_card.findChild(QLabel, "sessions_value").setText(str(sessions))
                self.ratio_card.findChild(QLabel, "ratio_value").setText(f"{ratio}%")
        except Exception as e:
            print(f"[HomeTab] Error fetching daily stats: {e}")

        # Active competitions
        try:
            comp_response = self.network_client.get_active_competition_leaderboard()
            if comp_response.get("status") == "success":
                competitions = comp_response.get("competitions", [])

                # Clear old cards
                while self.comps_container.count():
                    item = self.comps_container.takeAt(0)
                    if item.widget():
                        item.widget().deleteLater()

                if competitions:
                    for comp in competitions:
                        card = self._make_comp_card(comp)
                        self.comps_container.addWidget(card)
                else:
                    no_lbl = QLabel("No active competitions. Join one from the Competitions tab!")
                    no_lbl.setStyleSheet("color: #64748b; font-size: 13px; padding: 20px 0;")
                    self.comps_container.addWidget(no_lbl)
        except Exception as e:
            print(f"[HomeTab] Error fetching competitions: {e}")

    def showEvent(self, event):
        super().showEvent(event)
        self.refresh_data()
