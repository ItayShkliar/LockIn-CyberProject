"""
Home Tab — Dashboard overview with daily stats cards and active competition list.
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QScrollArea,
                             QFrame, QHBoxLayout, QGraphicsDropShadowEffect)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QColor
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
        layout.setContentsMargins(44, 44, 44, 44)
        layout.setSpacing(28)

        # ── Greeting ──
        self.greeting_label = QLabel("Hello, User")
        self.greeting_label.setObjectName("Title")
        layout.addWidget(self.greeting_label)

        self.subtitle_label = QLabel("Let's stay focused today.")
        self.subtitle_label.setStyleSheet("font-size: 14px; color: #475569; margin-bottom: 4px;")
        layout.addWidget(self.subtitle_label)

        # ── Stats Row (3 cards) ──
        stats_grid = QHBoxLayout()
        stats_grid.setSpacing(16)

        self.focus_card = self._make_stat_card(
            "TODAY'S FOCUS", "00:00:00", "#3b82f6", "focus_value", "⏱"
        )
        stats_grid.addWidget(self.focus_card)

        self.sessions_card = self._make_stat_card(
            "SESSIONS", "0", "#10b981", "sessions_value", "📋"
        )
        stats_grid.addWidget(self.sessions_card)

        self.ratio_card = self._make_stat_card(
            "FOCUS RATIO", "0%", "#a855f7", "ratio_value", "🎯"
        )
        stats_grid.addWidget(self.ratio_card)

        layout.addLayout(stats_grid)

        # ── Active Competitions Section ──
        comp_header = QLabel("ACTIVE COMPETITIONS")
        comp_header.setObjectName("SectionHeader")
        comp_header.setStyleSheet("margin-top: 12px; padding-left: 4px;")
        layout.addWidget(comp_header)

        self.comps_container = QVBoxLayout()
        self.comps_container.setSpacing(12)

        self.no_comps_label = QLabel("No active competitions. Join one from the Competitions tab!")
        self.no_comps_label.setStyleSheet("color: #334155; font-size: 13px; padding: 20px 0;")
        self.comps_container.addWidget(self.no_comps_label)

        layout.addLayout(self.comps_container)
        layout.addStretch()

        scroll.setWidget(inner)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

    def _make_stat_card(self, title: str, value: str, color: str,
                        obj_name: str, icon: str = "") -> QFrame:
        card = QFrame()
        card.setObjectName("Card")
        card.setMinimumHeight(110)
        cl = QVBoxLayout(card)
        cl.setContentsMargins(22, 18, 22, 18)
        cl.setSpacing(6)

        # Header row with icon
        header_row = QHBoxLayout()
        lbl = QLabel(title)
        lbl.setStyleSheet(
            "font-size: 10px; font-weight: 700; color: #475569; "
            "letter-spacing: 1.5px; background: transparent;"
        )
        header_row.addWidget(lbl)
        header_row.addStretch()
        if icon:
            icon_lbl = QLabel(icon)
            icon_lbl.setStyleSheet("font-size: 16px; background: transparent;")
            header_row.addWidget(icon_lbl)
        cl.addLayout(header_row)

        val = QLabel(value)
        val.setObjectName(obj_name)
        val.setStyleSheet(
            f"font-size: 30px; font-weight: 800; color: {color}; "
            f"letter-spacing: -0.5px; background: transparent;"
        )
        cl.addWidget(val)

        # Subtle glow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(color))
        shadow.setOffset(0, 2)
        card.setGraphicsEffect(shadow)

        return card

    def _make_comp_card(self, comp: dict) -> QFrame:
        card = QFrame()
        card.setObjectName("Card")
        card.setStyleSheet("""
            QFrame#Card {
                border-left: 3px solid rgba(59, 130, 246, 0.5);
            }
        """)
        cl = QHBoxLayout(card)
        cl.setContentsMargins(18, 14, 18, 14)
        cl.setSpacing(16)

        # Left: Info
        info_layout = QVBoxLayout()
        info_layout.setSpacing(4)

        name_lbl = QLabel(comp.get("name", "Competition"))
        name_lbl.setStyleSheet(
            "font-size: 15px; font-weight: 700; color: #f8fafc; background: transparent;"
        )
        info_layout.addWidget(name_lbl)

        focus_apps = comp.get("focus_apps")
        if focus_apps:
            apps_text = ", ".join(focus_apps)
            apps_lbl = QLabel(f"Focus: {apps_text}")
            apps_lbl.setStyleSheet(
                "font-size: 11px; color: #38bdf8; font-weight: 500; background: transparent;"
            )
            info_layout.addWidget(apps_lbl)
        else:
            gen_lbl = QLabel("General Competition")
            gen_lbl.setStyleSheet("font-size: 11px; color: #475569; background: transparent;")
            info_layout.addWidget(gen_lbl)

        time_lbl = QLabel(f"Your time: {comp.get('my_focus_time_formatted', '00:00:00')}")
        time_lbl.setStyleSheet("font-size: 12px; color: #64748b; background: transparent;")
        info_layout.addWidget(time_lbl)

        cl.addLayout(info_layout, stretch=1)

        # Right: Rank badge
        rank = comp.get("my_rank", "?")
        total = comp.get("total_participants", "?")
        rank_frame = QFrame()
        rank_frame.setStyleSheet("background: transparent; border: none;")
        rank_layout = QVBoxLayout(rank_frame)
        rank_layout.setContentsMargins(12, 8, 12, 8)
        rank_layout.setSpacing(2)
        rank_layout.setAlignment(Qt.AlignCenter)

        rank_color = ("#fbbf24" if rank == 1 else
                      "#94a3b8" if rank == 2 else
                      "#cd7f32" if rank == 3 else "#475569")
        rank_num = QLabel(f"#{rank}" if rank else "?")
        rank_num.setStyleSheet(
            f"font-size: 26px; font-weight: 800; color: {rank_color}; background: transparent;"
        )
        rank_num.setAlignment(Qt.AlignCenter)
        rank_layout.addWidget(rank_num)

        of_lbl = QLabel(f"of {total}")
        of_lbl.setStyleSheet("font-size: 10px; color: #334155; background: transparent;")
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
                    no_lbl.setStyleSheet("color: #334155; font-size: 13px; padding: 20px 0;")
                    self.comps_container.addWidget(no_lbl)
        except Exception as e:
            print(f"[HomeTab] Error fetching competitions: {e}")

    def showEvent(self, event):
        super().showEvent(event)
        self.refresh_data()
