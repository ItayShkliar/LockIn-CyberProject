from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QScrollArea, QFrame)
from PyQt5.QtCore import Qt
from datetime import datetime # <-- NEW IMPORT

class LeaderboardTab(QWidget):
    def __init__(self, network_client):
        super().__init__()
        self.network_client = network_client
        self._init_ui()

    def _init_ui(self):
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(30)

        # ==========================================
        # LEFT PANEL: List of User's Rooms
        # ==========================================
        left_panel = QVBoxLayout()
        
        title = QLabel("🏆 My Rooms")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: white;")
        left_panel.addWidget(title)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        
        self.rooms_container = QWidget()
        self.rooms_container.setStyleSheet("background-color: transparent;")
        self.rooms_layout = QVBoxLayout(self.rooms_container)
        self.rooms_layout.setAlignment(Qt.AlignTop)
        
        self.scroll_area.setWidget(self.rooms_container)
        left_panel.addWidget(self.scroll_area)
        
        self.refresh_rooms_btn = QPushButton("🔄 Refresh Rooms")
        self.refresh_rooms_btn.setFixedHeight(40)
        self.refresh_rooms_btn.setStyleSheet("background-color: #4F545C; color: white; font-weight: bold; border-radius: 5px;")
        self.refresh_rooms_btn.clicked.connect(self.load_user_rooms)
        left_panel.addWidget(self.refresh_rooms_btn)

        # ==========================================
        # RIGHT PANEL: The Leaderboard Table
        # ==========================================
        right_panel = QVBoxLayout()
        
        self.table_title = QLabel("📊 Select a room to view stats")
        self.table_title.setStyleSheet("font-size: 24px; font-weight: bold; color: #7289DA;")
        right_panel.addWidget(self.table_title)

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Rank", "Username", "Total Focus Time"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #2F3136;
                color: white;
                gridline-color: #202225;
                border-radius: 5px;
            }
            QHeaderView::section {
                background-color: #202225;
                color: #7289DA;
                font-weight: bold;
                padding: 5px;
            }
        """)
        right_panel.addWidget(self.table)

        main_layout.addLayout(left_panel, 1)
        main_layout.addLayout(right_panel, 2)
        
        self.setLayout(main_layout)

    def showEvent(self, event):
        super().showEvent(event)
        self.load_user_rooms()

    def load_user_rooms(self):
        # 1. Clear existing cards
        for i in reversed(range(self.rooms_layout.count())): 
            widget = self.rooms_layout.itemAt(i).widget()
            if widget is not None: 
                widget.deleteLater()

        # 2. Fetch from server
        response = self.network_client.get_user_competitions()
        if response.get("status") != "success":
            return

        rooms = response.get("rooms", [])
        if not rooms:
            no_rooms = QLabel("You are not in any rooms yet.\nGo to the Competitions tab to join one!")
            no_rooms.setStyleSheet("color: #B9BBBE; font-size: 14px;")
            self.rooms_layout.addWidget(no_rooms)
            return

        # 3. Build UI Cards
        for room in rooms:
            card = QFrame()
            card.setStyleSheet("background-color: #202225; border-radius: 8px; padding: 15px; margin-bottom: 10px;")
            card_layout = QVBoxLayout(card)
            
            # Name and Code
            name_label = QLabel(f"{room['name']} (Code: {room['id']})")
            name_label.setStyleSheet("color: #43B581; font-size: 16px; font-weight: bold;")
            card_layout.addWidget(name_label)
            
            # Description
            desc = room.get('desc') or "No description provided."
            desc_label = QLabel(desc)
            desc_label.setStyleSheet("color: #B9BBBE; font-size: 12px;")
            desc_label.setWordWrap(True)
            card_layout.addWidget(desc_label)

            # ---> NEW: DATES AND STATUS <---
            start_str = room.get('start', '')
            end_str = room.get('end', '')
            
            try:
                # Parse strings into datetime objects
                start_dt = datetime.strptime(start_str, "%Y-%m-%d %H:%M:%S")
                end_dt = datetime.strptime(end_str, "%Y-%m-%d %H:%M:%S")
                now = datetime.now()
                
                # Determine status
                if now < start_dt:
                    status_text = "⏳ Not Started Yet"
                    status_color = "#FAA61A" # Yellow
                elif start_dt <= now <= end_dt:
                    status_text = "🟢 Active Now"
                    status_color = "#43B581" # Green
                else:
                    status_text = "🔴 Ended"
                    status_color = "#E74C3C" # Red
                    
                # Format to look clean: "Oct 14, 15:30"
                fmt_start = start_dt.strftime("%b %d, %H:%M")
                fmt_end = end_dt.strftime("%b %d, %H:%M")
                date_display = f"{status_text}\n{fmt_start} ➔ {fmt_end}"
            except Exception:
                # Fallback if dates are improperly formatted
                date_display = f"Start: {start_str} | End: {end_str}"
                status_color = "#B9BBBE"

            date_label = QLabel(date_display)
            date_label.setStyleSheet(f"color: {status_color}; font-size: 12px; font-weight: bold; margin-top: 5px;")
            card_layout.addWidget(date_label)
            
            # Button
            view_btn = QPushButton("View Stats")
            view_btn.setStyleSheet("background-color: #7289DA; color: white; border-radius: 4px; padding: 5px; margin-top: 10px;")
            view_btn.clicked.connect(lambda checked, r_id=room['id'], r_name=room['name']: self.load_leaderboard(r_id, r_name))
            card_layout.addWidget(view_btn)
            
            self.rooms_layout.addWidget(card)

    def load_leaderboard(self, room_id: int, room_name: str):
        self.table_title.setText(f"📊 {room_name} Leaderboard")
        self.table.setRowCount(0) 
        
        response = self.network_client.get_leaderboard(room_id)
        
        if response.get("status") == "success":
            leaderboard = response.get("leaderboard", [])
            self.table.setRowCount(len(leaderboard))
            
            for row_idx, user in enumerate(leaderboard):
                rank = user.get("rank", row_idx + 1)
                username = user.get("username", "Unknown")
                
                focus_seconds = user.get("focus_time", 0)
                time_str = f"{focus_seconds // 3600:02}:{(focus_seconds % 3600) // 60:02}:{focus_seconds % 60:02}"
                
                self.table.setItem(row_idx, 0, QTableWidgetItem(f"#{rank}"))
                self.table.setItem(row_idx, 1, QTableWidgetItem(username))
                self.table.setItem(row_idx, 2, QTableWidgetItem(time_str))