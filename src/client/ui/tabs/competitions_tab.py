"""
Competitions Tab (v2)
Allows users to create, join, leave, and browse competitions.
Shows participant count, status, and public competition browser.
"""
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
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(30, 30, 30, 30)

        title = QLabel("Competitions")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: white;")
        main_layout.addWidget(title)

        # Sub-tabs: My Rooms | Browse Public | Create
        self.sub_tabs = QTabWidget()
        self.sub_tabs.setStyleSheet("""
            QTabWidget::pane { border: 1px solid #2F3136; background: #2F3136; border-radius: 8px; }
            QTabBar::tab { background: #202225; color: #B9BBBE; padding: 8px 20px; border-radius: 4px; }
            QTabBar::tab:selected { background: #7289DA; color: white; font-weight: bold; }
        """)

        self.sub_tabs.addTab(self._build_my_rooms_tab(), "My Competitions")
        self.sub_tabs.addTab(self._build_browse_tab(), "Browse Public")
        self.sub_tabs.addTab(self._build_create_tab(), "Create New")
        self.sub_tabs.addTab(self._build_join_tab(), "Join by Code")

        main_layout.addWidget(self.sub_tabs)
        self.setLayout(main_layout)

    # -----------------------------------------------------------------------
    # My Rooms tab
    # -----------------------------------------------------------------------

    def _build_my_rooms_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(15, 15, 15, 15)

        refresh_btn = QPushButton("Refresh")
        refresh_btn.setFixedWidth(120)
        refresh_btn.setStyleSheet("background-color: #7289DA; color: white; border-radius: 4px; padding: 6px;")
        refresh_btn.clicked.connect(self._load_my_rooms)
        layout.addWidget(refresh_btn, alignment=Qt.AlignRight)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none; background: transparent;")

        self.rooms_container = QWidget()
        self.rooms_layout = QVBoxLayout(self.rooms_container)
        self.rooms_layout.setAlignment(Qt.AlignTop)
        self.rooms_layout.setSpacing(10)

        scroll.setWidget(self.rooms_container)
        layout.addWidget(scroll)
        return widget

    def _load_my_rooms(self):
        # Clear existing cards
        for i in reversed(range(self.rooms_layout.count())):
            w = self.rooms_layout.itemAt(i).widget()
            if w:
                w.deleteLater()

        response = self.network_client.get_user_competitions()
        if response.get("status") != "success":
            lbl = QLabel(f"Error: {response.get('message', 'Unknown error')}")
            lbl.setStyleSheet("color: #E74C3C; font-size: 14px;")
            self.rooms_layout.addWidget(lbl)
            return

        rooms = response.get("rooms", [])
        if not rooms:
            lbl = QLabel("You are not in any competitions yet.\nUse 'Browse Public' or 'Join by Code'.")
            lbl.setStyleSheet("color: #B9BBBE; font-size: 14px;")
            self.rooms_layout.addWidget(lbl)
            return

        for room in rooms:
            self.rooms_layout.addWidget(self._build_room_card(room))

    def _build_room_card(self, room: dict) -> QFrame:
        card = QFrame()
        card.setStyleSheet("""
            QFrame { background-color: #202225; border-radius: 8px; padding: 12px; }
            QFrame:hover { background-color: #2F3136; }
        """)
        layout = QVBoxLayout(card)

        # Header row
        header = QHBoxLayout()
        name_lbl = QLabel(f"{room['name']}  (Code: {room['id']})")
        name_lbl.setStyleSheet("color: #43B581; font-size: 16px; font-weight: bold;")
        header.addWidget(name_lbl)
        header.addStretch()

        # Status badge
        status = room.get("status", "active")
        status_colors = {"active": "#43B581", "ended": "#E74C3C", "pending": "#FAA61A"}
        status_lbl = QLabel(status.upper())
        status_lbl.setStyleSheet(f"color: {status_colors.get(status, '#B9BBBE')}; font-weight: bold; font-size: 12px;")
        header.addWidget(status_lbl)
        layout.addLayout(header)

        # Description
        desc = room.get("desc") or "No description."
        desc_lbl = QLabel(desc)
        desc_lbl.setStyleSheet("color: #B9BBBE; font-size: 12px;")
        desc_lbl.setWordWrap(True)
        layout.addWidget(desc_lbl)

        # Dates + participants
        try:
            start_dt = datetime.strptime(room.get("start", ""), "%Y-%m-%d %H:%M:%S")
            end_dt = datetime.strptime(room.get("end", ""), "%Y-%m-%d %H:%M:%S")
            now = datetime.now()
            if now < start_dt:
                status_text = "Not Started Yet"
                sc = "#FAA61A"
            elif start_dt <= now <= end_dt:
                status_text = "Active Now"
                sc = "#43B581"
            else:
                status_text = "Ended"
                sc = "#E74C3C"
            date_str = f"{start_dt.strftime('%b %d, %H:%M')} -> {end_dt.strftime('%b %d, %H:%M')}"
        except Exception:
            status_text = ""
            sc = "#B9BBBE"
            date_str = f"{room.get('start', '')} -> {room.get('end', '')}"

        info_row = QHBoxLayout()
        date_lbl = QLabel(date_str)
        date_lbl.setStyleSheet(f"color: {sc}; font-size: 12px;")
        info_row.addWidget(date_lbl)
        info_row.addStretch()

        participants_lbl = QLabel(f"Participants: {room.get('participant_count', '?')}")
        participants_lbl.setStyleSheet("color: #7289DA; font-size: 12px;")
        info_row.addWidget(participants_lbl)
        layout.addLayout(info_row)

        # My rank + focus time
        my_rank = room.get("my_rank")
        my_time = room.get("my_focus_time_formatted", "00:00:00")
        if my_rank:
            rank_lbl = QLabel(f"My Rank: #{my_rank}  |  My Focus: {my_time}")
            rank_lbl.setStyleSheet("color: #FAA61A; font-size: 12px; font-weight: bold;")
            layout.addWidget(rank_lbl)

        # Buttons
        btn_row = QHBoxLayout()
        view_btn = QPushButton("View Leaderboard")
        view_btn.setStyleSheet("background-color: #7289DA; color: white; border-radius: 4px; padding: 5px;")
        view_btn.clicked.connect(lambda _, rid=room["id"], rname=room["name"]: self._show_leaderboard(rid, rname))
        btn_row.addWidget(view_btn)

        leave_btn = QPushButton("Leave")
        leave_btn.setStyleSheet("background-color: #E74C3C; color: white; border-radius: 4px; padding: 5px;")
        leave_btn.clicked.connect(lambda _, rid=room["id"]: self._leave_competition(rid))
        btn_row.addWidget(leave_btn)
        layout.addLayout(btn_row)

        return card

    def _show_leaderboard(self, room_id: int, room_name: str):
        """Opens a leaderboard dialog for the selected competition."""
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QHeaderView
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Leaderboard - {room_name}")
        dialog.setMinimumSize(600, 400)
        dialog.setStyleSheet("background-color: #36393F; color: white;")
        dlayout = QVBoxLayout(dialog)

        title = QLabel(f"Leaderboard: {room_name}")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: white; padding: 10px;")
        dlayout.addWidget(title)

        table = QTableWidget()
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels(["Rank", "Username", "Focus Time", "Sessions", "Score"])
        table.setStyleSheet("""
            QTableWidget { background-color: #202225; color: white; border: none; }
            QHeaderView::section { background-color: #2F3136; color: white; font-weight: bold; padding: 6px; }
        """)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        dlayout.addWidget(table)

        response = self.network_client.get_leaderboard(room_id)
        if response.get("status") == "success":
            leaderboard = response.get("leaderboard", [])
            table.setRowCount(len(leaderboard))
            for i, entry in enumerate(leaderboard):
                rank = entry.get("rank", i + 1)
                medal = {1: "Gold  #1", 2: "Silver  #2", 3: "Bronze  #3"}.get(rank, f"#{rank}")
                table.setItem(i, 0, QTableWidgetItem(medal))
                table.setItem(i, 1, QTableWidgetItem(entry.get("username", "")))
                table.setItem(i, 2, QTableWidgetItem(entry.get("focus_time_formatted", "00:00:00")))
                table.setItem(i, 3, QTableWidgetItem(str(entry.get("sessions_count", 0))))
                table.setItem(i, 4, QTableWidgetItem(f"{entry.get('focus_score', 0):.1f}"))
        else:
            err = QLabel(f"Could not load leaderboard: {response.get('message', '')}")
            err.setStyleSheet("color: #E74C3C;")
            dlayout.addWidget(err)

        dialog.exec_()

    def _leave_competition(self, room_id: int):
        reply = QMessageBox.question(
            self, "Leave Competition",
            "Are you sure you want to leave this competition?\nYour progress will be lost.",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            response = self.network_client.leave_competition(room_id)
            if response.get("status") == "success":
                QMessageBox.information(self, "Left", "You have left the competition.")
                self._load_my_rooms()
            else:
                QMessageBox.warning(self, "Error", response.get("message", "Failed to leave"))

    # -----------------------------------------------------------------------
    # Browse Public tab
    # -----------------------------------------------------------------------

    def _build_browse_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(15, 15, 15, 15)

        refresh_btn = QPushButton("Refresh Public Competitions")
        refresh_btn.setStyleSheet("background-color: #7289DA; color: white; border-radius: 4px; padding: 6px;")
        refresh_btn.clicked.connect(self._load_public_competitions)
        layout.addWidget(refresh_btn, alignment=Qt.AlignRight)

        self.public_table = QTableWidget()
        self.public_table.setColumnCount(6)
        self.public_table.setHorizontalHeaderLabels(
            ["ID", "Name", "Creator", "Participants", "Status", "Action"]
        )
        self.public_table.setStyleSheet("""
            QTableWidget { background-color: #202225; color: white; border: none; border-radius: 5px; }
            QHeaderView::section { background-color: #2F3136; color: white; font-weight: bold; padding: 6px; }
            QTableWidget::item { padding: 4px; }
        """)
        self.public_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.public_table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.public_table)
        return widget

    def _load_public_competitions(self):
        response = self.network_client.get_public_competitions()
        if response.get("status") != "success":
            QMessageBox.warning(self, "Error", response.get("message", "Failed to load"))
            return
        competitions = response.get("competitions", [])
        self.public_table.setRowCount(len(competitions))
        for i, comp in enumerate(competitions):
            self.public_table.setItem(i, 0, QTableWidgetItem(str(comp.get("competition_id", ""))))
            self.public_table.setItem(i, 1, QTableWidgetItem(comp.get("name", "")))
            self.public_table.setItem(i, 2, QTableWidgetItem(comp.get("creator_name", "")))
            self.public_table.setItem(i, 3, QTableWidgetItem(str(comp.get("participant_count", 0))))
            self.public_table.setItem(i, 4, QTableWidgetItem(comp.get("status", "").upper()))
            join_btn = QPushButton("Join")
            join_btn.setStyleSheet("background-color: #43B581; color: white; border-radius: 3px; padding: 3px 8px;")
            comp_id = comp.get("competition_id")
            join_btn.clicked.connect(lambda _, cid=comp_id: self._quick_join(cid))
            self.public_table.setCellWidget(i, 5, join_btn)

    def _quick_join(self, competition_id: int):
        response = self.network_client.join_competition(competition_id)
        if response.get("status") == "success":
            QMessageBox.information(self, "Joined!", response.get("message", "Joined successfully"))
            self._load_my_rooms()
            self.sub_tabs.setCurrentIndex(0)
        else:
            QMessageBox.warning(self, "Error", response.get("message", "Failed to join"))

    # -----------------------------------------------------------------------
    # Create tab
    # -----------------------------------------------------------------------

    def _build_create_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        def lbl(text):
            l = QLabel(text)
            l.setStyleSheet("color: #B9BBBE; font-size: 13px;")
            return l

        def field(placeholder=""):
            f = QLineEdit()
            f.setPlaceholderText(placeholder)
            f.setStyleSheet("background-color: #202225; color: white; border: 1px solid #4F545C; border-radius: 4px; padding: 6px;")
            return f

        layout.addWidget(lbl("Competition Name *"))
        self.create_name = field("e.g. Study Warriors")
        layout.addWidget(self.create_name)

        layout.addWidget(lbl("Description"))
        self.create_desc = QTextEdit()
        self.create_desc.setPlaceholderText("Optional description...")
        self.create_desc.setMaximumHeight(80)
        self.create_desc.setStyleSheet("background-color: #202225; color: white; border: 1px solid #4F545C; border-radius: 4px; padding: 6px;")
        layout.addWidget(self.create_desc)

        date_row = QHBoxLayout()
        start_col = QVBoxLayout()
        start_col.addWidget(lbl("Start Date & Time *"))
        self.create_start = QDateTimeEdit(QDateTime.currentDateTime())
        self.create_start.setDisplayFormat("yyyy-MM-dd HH:mm")
        self.create_start.setStyleSheet("background-color: #202225; color: white; border: 1px solid #4F545C; border-radius: 4px; padding: 6px;")
        start_col.addWidget(self.create_start)
        date_row.addLayout(start_col)

        end_col = QVBoxLayout()
        end_col.addWidget(lbl("End Date & Time *"))
        self.create_end = QDateTimeEdit(QDateTime.currentDateTime().addDays(7))
        self.create_end.setDisplayFormat("yyyy-MM-dd HH:mm")
        self.create_end.setStyleSheet("background-color: #202225; color: white; border: 1px solid #4F545C; border-radius: 4px; padding: 6px;")
        end_col.addWidget(self.create_end)
        date_row.addLayout(end_col)
        layout.addLayout(date_row)

        options_row = QHBoxLayout()
        max_col = QVBoxLayout()
        max_col.addWidget(lbl("Max Participants (0 = unlimited)"))
        self.create_max = QSpinBox()
        self.create_max.setRange(0, 1000)
        self.create_max.setValue(0)
        self.create_max.setStyleSheet("background-color: #202225; color: white; border: 1px solid #4F545C; border-radius: 4px; padding: 6px;")
        max_col.addWidget(self.create_max)
        options_row.addLayout(max_col)

        pub_col = QVBoxLayout()
        pub_col.addWidget(lbl("Visibility"))
        self.create_public = QCheckBox("Public (visible to everyone)")
        self.create_public.setChecked(True)
        self.create_public.setStyleSheet("color: white;")
        pub_col.addWidget(self.create_public)
        options_row.addLayout(pub_col)
        layout.addLayout(options_row)

        create_btn = QPushButton("Create Competition")
        create_btn.setStyleSheet("background-color: #43B581; color: white; font-weight: bold; border-radius: 5px; padding: 10px;")
        create_btn.clicked.connect(self._create_competition)
        layout.addWidget(create_btn)

        layout.addStretch()
        return widget

    def _create_competition(self):
        name = self.create_name.text().strip()
        if not name:
            QMessageBox.warning(self, "Validation Error", "Competition name is required.")
            return
        start = self.create_start.dateTime().toString("yyyy-MM-dd HH:mm:ss")
        end = self.create_end.dateTime().toString("yyyy-MM-dd HH:mm:ss")
        if self.create_end.dateTime() <= self.create_start.dateTime():
            QMessageBox.warning(self, "Validation Error", "End date must be after start date.")
            return
        desc = self.create_desc.toPlainText().strip()
        max_p = self.create_max.value()
        is_public = self.create_public.isChecked()

        response = self.network_client.create_competition(
            name=name, start_date=start, end_date=end,
            description=desc, max_participants=max_p, is_public=is_public
        )
        if response.get("status") == "success":
            code = response.get("room_code", "?")
            QMessageBox.information(
                self, "Competition Created!",
                f"'{name}' created successfully!\n\nShare this code with friends: {code}"
            )
            self.create_name.clear()
            self.create_desc.clear()
            self._load_my_rooms()
            self.sub_tabs.setCurrentIndex(0)
        else:
            QMessageBox.warning(self, "Error", response.get("message", "Failed to create"))

    # -----------------------------------------------------------------------
    # Join by Code tab
    # -----------------------------------------------------------------------

    def _build_join_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setAlignment(Qt.AlignTop)

        title = QLabel("Join a Competition by Code")
        title.setStyleSheet("color: white; font-size: 18px; font-weight: bold;")
        layout.addWidget(title)

        layout.addSpacing(20)

        lbl = QLabel("Enter the competition code shared by the host:")
        lbl.setStyleSheet("color: #B9BBBE; font-size: 13px;")
        layout.addWidget(lbl)

        self.join_code_input = QLineEdit()
        self.join_code_input.setPlaceholderText("e.g. 42")
        self.join_code_input.setStyleSheet(
            "background-color: #202225; color: white; border: 1px solid #4F545C; "
            "border-radius: 4px; padding: 8px; font-size: 16px;"
        )
        layout.addWidget(self.join_code_input)

        join_btn = QPushButton("Join Competition")
        join_btn.setStyleSheet(
            "background-color: #7289DA; color: white; font-weight: bold; "
            "border-radius: 5px; padding: 10px; font-size: 14px;"
        )
        join_btn.clicked.connect(self._join_competition)
        layout.addWidget(join_btn)

        layout.addStretch()
        return widget

    def _join_competition(self):
        code_text = self.join_code_input.text().strip()
        if not code_text:
            QMessageBox.warning(self, "Input Required", "Please enter a competition code.")
            return
        try:
            code = int(code_text)
        except ValueError:
            QMessageBox.warning(self, "Invalid Code", "Competition code must be a number.")
            return

        response = self.network_client.join_competition(code)
        if response.get("status") == "success":
            QMessageBox.information(self, "Joined!", response.get("message", "Joined successfully!"))
            self.join_code_input.clear()
            self._load_my_rooms()
            self.sub_tabs.setCurrentIndex(0)
        else:
            QMessageBox.warning(self, "Error", response.get("message", "Failed to join"))

    # -----------------------------------------------------------------------
    # Qt lifecycle
    # -----------------------------------------------------------------------

    def showEvent(self, event):
        super().showEvent(event)
        self._load_my_rooms()
