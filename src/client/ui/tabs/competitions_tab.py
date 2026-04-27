from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QDateTimeEdit, QTextEdit, QMessageBox, QFrame,
    QScrollArea, QTabWidget, QCheckBox, QSpinBox, QTableWidget,
    QTableWidgetItem, QHeaderView
)
from PyQt5.QtCore import Qt, QDateTime
from datetime import datetime

class CompetitionsTab(QWidget):
    def __init__(self, network_client):
        super().__init__()
        self.network_client = network_client
        self._build_ui()

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(20)

        title = QLabel("Competitions")
        title.setObjectName("Title")
        main_layout.addWidget(title)

        self.sub_tabs = QTabWidget()
        self.sub_tabs.setUsesScrollButtons(True) # Allow scrolling if tabs don't fit
        # The global stylesheet handles QTabWidget generally, 
        # but we can add some local overrides if needed.
        self.sub_tabs.addTab(self._build_my_rooms_tab(), "My Competitions")
        self.sub_tabs.addTab(self._build_browse_tab(), "Browse Public")
        self.sub_tabs.addTab(self._build_create_tab(), "Create New")
        self.sub_tabs.addTab(self._build_join_tab(), "Join by Code")

        main_layout.addWidget(self.sub_tabs)

    def _build_my_rooms_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)

        top_row = QHBoxLayout()
        top_row.addWidget(QLabel("YOUR COMPETING GROUPS"))
        refresh_btn = QPushButton("Refresh")
        refresh_btn.setProperty("theme", "primary")
        refresh_btn.setFixedWidth(100)
        refresh_btn.clicked.connect(self._load_my_rooms)
        top_row.addWidget(refresh_btn)
        layout.addLayout(top_row)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none; background: transparent;")

        self.rooms_container = QWidget()
        self.rooms_layout = QVBoxLayout(self.rooms_container)
        self.rooms_layout.setAlignment(Qt.AlignTop)
        self.rooms_layout.setSpacing(15)

        scroll.setWidget(self.rooms_container)
        layout.addWidget(scroll)
        return widget

    def _load_my_rooms(self):
        for i in reversed(range(self.rooms_layout.count())):
            w = self.rooms_layout.itemAt(i).widget()
            if w: w.deleteLater()

        response = self.network_client.get_user_competitions()
        if response.get("status") != "success":
            lbl = QLabel(f"Error: {response.get('message', 'Unknown error')}")
            lbl.setStyleSheet("color: #ef4444;")
            self.rooms_layout.addWidget(lbl)
            return

        rooms = response.get("rooms", [])
        if not rooms:
            lbl = QLabel("You haven't joined any competitions yet.")
            lbl.setObjectName("Subtitle")
            self.rooms_layout.addWidget(lbl)
            return

        for room in rooms:
            self.rooms_layout.addWidget(self._build_room_card(room))

    def _build_room_card(self, room: dict) -> QFrame:
        card = QFrame()
        card.setObjectName("Card")
        layout = QVBoxLayout(card)
        layout.setSpacing(10)

        header = QHBoxLayout()
        name_lbl = QLabel(room['name'])
        name_lbl.setStyleSheet("font-size: 18px; font-weight: bold; color: #3b82f6;")
        header.addWidget(name_lbl)
        header.addStretch()

        status = room.get("status", "active")
        status_lbl = QLabel(status.upper())
        color = "#10b981" if status == "active" else "#ef4444" if status == "ended" else "#f59e0b"
        status_lbl.setStyleSheet(f"color: {color}; font-weight: bold;")
        header.addWidget(status_lbl)
        layout.addLayout(header)

        desc = room.get("desc") or "No description."
        desc_lbl = QLabel(desc)
        desc_lbl.setObjectName("Subtitle")
        desc_lbl.setWordWrap(True)
        layout.addWidget(desc_lbl)

        info_row = QHBoxLayout()
        participants_lbl = QLabel(f"👥 {room.get('participant_count', '?')} participants")
        participants_lbl.setObjectName("Subtitle")
        info_row.addWidget(participants_lbl)
        info_row.addStretch()
        
        my_time = room.get("my_focus_time_formatted", "00:00:00")
        time_lbl = QLabel(f"🕒 Your Time: {my_time}")
        time_lbl.setStyleSheet("color: #f8fafc; font-weight: 500;")
        info_row.addWidget(time_lbl)
        layout.addLayout(info_row)

        btn_row = QHBoxLayout()
        view_btn = QPushButton("Leaderboard")
        view_btn.setProperty("theme", "primary")
        view_btn.clicked.connect(lambda _, rid=room["id"], rname=room["name"]: self._show_leaderboard(rid, rname))
        btn_row.addWidget(view_btn)

        leave_btn = QPushButton("Leave")
        leave_btn.setProperty("theme", "danger")
        leave_btn.clicked.connect(lambda _, rid=room["id"]: self._leave_competition(rid))
        btn_row.addWidget(leave_btn)
        layout.addLayout(btn_row)

        return card

    def _show_leaderboard(self, room_id: int, room_name: str):
        from PyQt5.QtWidgets import QDialog
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Leaderboard - {room_name}")
        dialog.setMinimumSize(600, 500)
        dlayout = QVBoxLayout(dialog)
        dlayout.setContentsMargins(20, 20, 20, 20)

        title = QLabel(f"Leaderboard: {room_name}")
        title.setObjectName("Title")
        dlayout.addWidget(title)

        table = QTableWidget()
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels(["Rank", "User", "Focus Time", "Sessions", "Score"])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive) # Allow user to resize
        table.horizontalHeader().setStretchLastSection(True)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.verticalHeader().setDefaultSectionSize(40) # Ensure enough vertical space
        dlayout.addWidget(table)

        response = self.network_client.get_leaderboard(room_id)
        if response.get("status") == "success":
            leaderboard = response.get("leaderboard", [])
            table.setRowCount(len(leaderboard))
            for i, entry in enumerate(leaderboard):
                rank = entry.get("rank", i + 1)
                table.setItem(i, 0, QTableWidgetItem(f"#{rank}"))
                table.setItem(i, 1, QTableWidgetItem(entry.get("username", "")))
                table.setItem(i, 2, QTableWidgetItem(entry.get("focus_time_formatted", "00:00:00")))
                table.setItem(i, 3, QTableWidgetItem(str(entry.get("sessions_count", 0))))
                table.setItem(i, 4, QTableWidgetItem(f"{entry.get('focus_score', 0):.1f}"))
        else:
            err = QLabel(f"Error: {response.get('message', '')}")
            err.setStyleSheet("color: #ef4444;")
            dlayout.addWidget(err)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.close)
        dlayout.addWidget(close_btn)
        dialog.exec_()

    def _leave_competition(self, room_id: int):
        reply = QMessageBox.question(self, "Leave?", "Are you sure you want to leave?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            response = self.network_client.leave_competition(room_id)
            if response.get("status") == "success":
                self._load_my_rooms()
            else:
                QMessageBox.warning(self, "Error", response.get("message", "Failed to leave"))

    def _build_browse_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)

        top = QHBoxLayout()
        top.addWidget(QLabel("PUBLIC COMPETITIONS"))
        refresh_btn = QPushButton("Refresh List")
        refresh_btn.setProperty("theme", "primary")
        refresh_btn.clicked.connect(self._load_public_competitions)
        top.addWidget(refresh_btn)
        layout.addLayout(top)

        self.public_table = QTableWidget()
        self.public_table.setColumnCount(6)
        self.public_table.setHorizontalHeaderLabels(["ID", "Name", "Creator", "Users", "Status", "Action"])
        self.public_table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.public_table.horizontalHeader().setStretchLastSection(True)
        self.public_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.public_table.verticalHeader().setDefaultSectionSize(45)
        layout.addWidget(self.public_table)
        return widget

    def _load_public_competitions(self):
        response = self.network_client.get_public_competitions()
        if response.get("status") != "success": return
        competitions = response.get("competitions", [])
        self.public_table.setRowCount(len(competitions))
        for i, comp in enumerate(competitions):
            self.public_table.setItem(i, 0, QTableWidgetItem(str(comp.get("competition_id", ""))))
            self.public_table.setItem(i, 1, QTableWidgetItem(comp.get("name", "")))
            self.public_table.setItem(i, 2, QTableWidgetItem(comp.get("creator_name", "")))
            self.public_table.setItem(i, 3, QTableWidgetItem(str(comp.get("participant_count", 0))))
            self.public_table.setItem(i, 4, QTableWidgetItem(comp.get("status", "").upper()))
            join_btn = QPushButton("Join")
            join_btn.setProperty("theme", "success")
            comp_id = comp.get("competition_id")
            join_btn.clicked.connect(lambda _, cid=comp_id: self._quick_join(cid))
            self.public_table.setCellWidget(i, 5, join_btn)

    def _quick_join(self, competition_id: int):
        response = self.network_client.join_competition(competition_id)
        if response.get("status") == "success":
            self._load_my_rooms()
            self.sub_tabs.setCurrentIndex(0)
        else:
            QMessageBox.warning(self, "Error", response.get("message", "Failed to join"))

    def _build_create_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(40, 20, 40, 20)
        layout.setSpacing(15)

        layout.addWidget(QLabel("Name *"))
        self.create_name = QLineEdit()
        layout.addWidget(self.create_name)

        layout.addWidget(QLabel("Description"))
        self.create_desc = QTextEdit()
        self.create_desc.setMaximumHeight(100)
        layout.addWidget(self.create_desc)

        date_row = QHBoxLayout()
        v1 = QVBoxLayout(); v1.addWidget(QLabel("Start Time")); self.create_start = QDateTimeEdit(QDateTime.currentDateTime()); v1.addWidget(self.create_start); date_row.addLayout(v1)
        v2 = QVBoxLayout(); v2.addWidget(QLabel("End Time")); self.create_end = QDateTimeEdit(QDateTime.currentDateTime().addDays(7)); v2.addWidget(self.create_end); date_row.addLayout(v2)
        layout.addLayout(date_row)

        options = QHBoxLayout()
        v3 = QVBoxLayout(); v3.addWidget(QLabel("Max Users (0=inf)")); self.create_max = QSpinBox(); v3.addWidget(self.create_max); options.addLayout(v3)
        self.create_public = QCheckBox("Public Competition")
        self.create_public.setChecked(True)
        options.addWidget(self.create_public)
        layout.addLayout(options)

        create_btn = QPushButton("Create Competition")
        create_btn.setProperty("theme", "success")
        create_btn.setFixedHeight(50)
        create_btn.clicked.connect(self._create_competition)
        layout.addWidget(create_btn)
        layout.addStretch()
        return widget

    def _create_competition(self):
        name = self.create_name.text().strip()
        if not name: return
        start = self.create_start.dateTime().toString("yyyy-MM-dd HH:mm:ss")
        end = self.create_end.dateTime().toString("yyyy-MM-dd HH:mm:ss")
        response = self.network_client.create_competition(
            name=name, start_date=start, end_date=end,
            description=self.create_desc.toPlainText().strip(),
            max_participants=self.create_max.value(), is_public=self.create_public.isChecked()
        )
        if response.get("status") == "success":
            self._load_my_rooms()
            self.sub_tabs.setCurrentIndex(0)

    def _build_join_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)

        layout.addWidget(QLabel("Enter Room Code:"))
        self.join_code_input = QLineEdit()
        self.join_code_input.setPlaceholderText("Code provided by host...")
        self.join_code_input.setFixedHeight(50)
        layout.addWidget(self.join_code_input)

        join_btn = QPushButton("Join Room")
        join_btn.setProperty("theme", "primary")
        join_btn.setFixedHeight(50)
        join_btn.clicked.connect(self._join_competition)
        layout.addWidget(join_btn)
        layout.addStretch()
        return widget

    def _join_competition(self):
        code = self.join_code_input.text().strip()
        if not code: return
        response = self.network_client.join_competition(int(code) if code.isdigit() else 0)
        if response.get("status") == "success":
            self._load_my_rooms()
            self.sub_tabs.setCurrentIndex(0)

    def showEvent(self, event):
        super().showEvent(event)
        self._load_my_rooms()
