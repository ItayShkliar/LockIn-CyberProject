"""
Competitions Tab — Create, browse, join, and manage competitions.
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QDateTimeEdit, QTextEdit, QMessageBox, QFrame,
    QScrollArea, QTabWidget, QCheckBox, QSpinBox, QTableWidget,
    QTableWidgetItem, QHeaderView, QListWidget, QListWidgetItem
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
        main_layout.setContentsMargins(44, 44, 44, 44)
        main_layout.setSpacing(24)

        title = QLabel("Competitions")
        title.setObjectName("Title")
        main_layout.addWidget(title)

        subtitle = QLabel("Compete with friends and climb the leaderboard.")
        subtitle.setStyleSheet("color: #475569; font-size: 13px; margin-bottom: 4px;")
        main_layout.addWidget(subtitle)

        self.sub_tabs = QTabWidget()
        self.sub_tabs.setUsesScrollButtons(True)
        self.sub_tabs.addTab(self._build_my_rooms_tab(), "My Competitions")
        self.sub_tabs.addTab(self._build_browse_tab(), "Browse Public")
        self.sub_tabs.addTab(self._build_create_tab(), "Create New")
        self.sub_tabs.addTab(self._build_join_tab(), "Join by Code")

        main_layout.addWidget(self.sub_tabs)

    def _build_my_rooms_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 24, 20, 20)
        layout.setSpacing(16)

        top_row = QHBoxLayout()
        header = QLabel("YOUR COMPETITIONS")
        header.setObjectName("SectionHeader")
        top_row.addWidget(header)
        top_row.addStretch()

        refresh_btn = QPushButton("↻  Refresh")
        refresh_btn.setProperty("theme", "primary")
        refresh_btn.setFixedWidth(110)
        refresh_btn.setFixedHeight(34)
        refresh_btn.setCursor(Qt.PointingHandCursor)
        refresh_btn.clicked.connect(self._load_my_rooms)
        top_row.addWidget(refresh_btn)
        layout.addLayout(top_row)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        self.rooms_container = QWidget()
        self.rooms_layout = QVBoxLayout(self.rooms_container)
        self.rooms_layout.setAlignment(Qt.AlignTop)
        self.rooms_layout.setSpacing(12)

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
            lbl.setStyleSheet("color: #f87171; font-size: 13px;")
            self.rooms_layout.addWidget(lbl)
            return

        rooms = response.get("rooms", [])
        if not rooms:
            lbl = QLabel("You haven't joined any competitions yet.")
            lbl.setStyleSheet("color: #334155; font-size: 13px; padding: 20px 0;")
            self.rooms_layout.addWidget(lbl)
            return

        for room in rooms:
            self.rooms_layout.addWidget(self._build_room_card(room))

    def _build_room_card(self, room: dict) -> QFrame:
        card = QFrame()
        card.setObjectName("Card")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(10)

        header = QHBoxLayout()
        name_lbl = QLabel(room['name'])
        name_lbl.setStyleSheet(
            "font-size: 16px; font-weight: 700; color: #60a5fa; background: transparent;"
        )
        header.addWidget(name_lbl)
        header.addStretch()

        status = room.get("status", "active")
        status_colors = {
            "active": ("#34d399", "rgba(16, 185, 129, 0.1)"),
            "ended":  ("#f87171", "rgba(239, 68, 68, 0.1)"),
            "pending": ("#fbbf24", "rgba(251, 191, 36, 0.1)"),
        }
        fg, bg = status_colors.get(status, ("#475569", "transparent"))
        status_lbl = QLabel(status.upper())
        status_lbl.setStyleSheet(
            f"color: {fg}; background: {bg}; font-weight: 700; font-size: 10px; "
            f"padding: 3px 10px; border-radius: 6px; letter-spacing: 1px;"
        )
        header.addWidget(status_lbl)
        layout.addLayout(header)

        desc = room.get("desc") or "No description."
        desc_lbl = QLabel(desc)
        desc_lbl.setStyleSheet("color: #475569; font-size: 12px;")
        desc_lbl.setWordWrap(True)
        layout.addWidget(desc_lbl)

        info_row = QHBoxLayout()
        participants_lbl = QLabel(f"👥 {room.get('participant_count', '?')} participants")
        participants_lbl.setStyleSheet("color: #475569; font-size: 12px; background: transparent;")
        info_row.addWidget(participants_lbl)
        info_row.addStretch()

        my_rank = room.get("my_rank")
        if my_rank:
            rank_lbl = QLabel(f"Rank #{my_rank}")
            rank_color = ("#fbbf24" if my_rank == 1 else
                          "#94a3b8" if my_rank == 2 else
                          "#cd7f32" if my_rank == 3 else "#475569")
            rank_lbl.setStyleSheet(
                f"color: {rank_color}; font-weight: 700; font-size: 12px; background: transparent;"
            )
            info_row.addWidget(rank_lbl)

        my_time = room.get("my_focus_time_formatted", "00:00:00")
        time_lbl = QLabel(f"⏱ {my_time}")
        time_lbl.setStyleSheet(
            "color: #e2e8f0; font-weight: 600; font-size: 12px; background: transparent;"
        )
        info_row.addWidget(time_lbl)
        layout.addLayout(info_row)

        # Show focus apps if app-specific competition
        focus_apps = room.get("focus_apps")
        if focus_apps:
            apps_text = ", ".join(focus_apps)
            fa_lbl = QLabel(f"🎯 {apps_text}")
            fa_lbl.setStyleSheet(
                "color: #38bdf8; font-size: 11px; font-weight: 500; background: transparent;"
            )
            layout.addWidget(fa_lbl)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        view_btn = QPushButton("📊  Leaderboard")
        view_btn.setProperty("theme", "primary")
        view_btn.setFixedHeight(34)
        view_btn.setCursor(Qt.PointingHandCursor)
        view_btn.clicked.connect(lambda _, rid=room["id"], rname=room["name"]: self._show_leaderboard(rid, rname))
        btn_row.addWidget(view_btn)

        leave_btn = QPushButton("Leave")
        leave_btn.setProperty("theme", "ghost")
        leave_btn.setFixedHeight(34)
        leave_btn.setCursor(Qt.PointingHandCursor)
        leave_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: 1px solid rgba(239, 68, 68, 0.2);
                color: #64748b;
                font-size: 12px;
                border-radius: 8px;
            }
            QPushButton:hover {
                background: rgba(239, 68, 68, 0.08);
                color: #f87171;
            }
        """)
        leave_btn.clicked.connect(lambda _, rid=room["id"]: self._leave_competition(rid))
        btn_row.addWidget(leave_btn)
        layout.addLayout(btn_row)

        return card

    def _show_leaderboard(self, room_id: int, room_name: str):
        from PyQt5.QtWidgets import QDialog
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Leaderboard — {room_name}")
        dialog.setMinimumSize(620, 500)
        dialog.setStyleSheet("background-color: #0a0f1e;")
        dlayout = QVBoxLayout(dialog)
        dlayout.setContentsMargins(24, 24, 24, 24)
        dlayout.setSpacing(16)

        title = QLabel(f"Leaderboard: {room_name}")
        title.setObjectName("Title")
        dlayout.addWidget(title)

        table = QTableWidget()
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels(["Rank", "User", "Focus Time", "Sessions", "Score"])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        table.horizontalHeader().setStretchLastSection(True)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.verticalHeader().setDefaultSectionSize(40)
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
            err.setStyleSheet("color: #f87171;")
            dlayout.addWidget(err)

        close_btn = QPushButton("Close")
        close_btn.setProperty("theme", "ghost")
        close_btn.setFixedHeight(36)
        close_btn.setCursor(Qt.PointingHandCursor)
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
        layout.setContentsMargins(20, 24, 20, 20)
        layout.setSpacing(16)

        top = QHBoxLayout()
        header = QLabel("PUBLIC COMPETITIONS")
        header.setObjectName("SectionHeader")
        top.addWidget(header)
        top.addStretch()

        refresh_btn = QPushButton("↻  Refresh")
        refresh_btn.setProperty("theme", "primary")
        refresh_btn.setFixedHeight(34)
        refresh_btn.setCursor(Qt.PointingHandCursor)
        refresh_btn.clicked.connect(self._load_public_competitions)
        top.addWidget(refresh_btn)
        layout.addLayout(top)

        self.public_table = QTableWidget()
        self.public_table.setColumnCount(6)
        self.public_table.setHorizontalHeaderLabels(["ID", "Name", "Creator", "Users", "Status", "Action"])
        self.public_table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.public_table.horizontalHeader().setStretchLastSection(True)
        self.public_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.public_table.verticalHeader().setDefaultSectionSize(44)
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
            join_btn.setFixedHeight(30)
            join_btn.setCursor(Qt.PointingHandCursor)
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
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(40, 24, 40, 24)
        layout.setSpacing(14)

        # Name
        name_label = QLabel("NAME")
        name_label.setObjectName("SectionHeader")
        layout.addWidget(name_label)

        self.create_name = QLineEdit()
        self.create_name.setPlaceholderText("Competition name...")
        self.create_name.setFixedHeight(40)
        layout.addWidget(self.create_name)

        # Description
        desc_label = QLabel("DESCRIPTION")
        desc_label.setObjectName("SectionHeader")
        layout.addWidget(desc_label)

        self.create_desc = QTextEdit()
        self.create_desc.setMaximumHeight(80)
        self.create_desc.setPlaceholderText("Optional description...")
        layout.addWidget(self.create_desc)

        # Date row
        date_label = QLabel("SCHEDULE")
        date_label.setObjectName("SectionHeader")
        layout.addWidget(date_label)

        date_row = QHBoxLayout()
        date_row.setSpacing(12)

        v1 = QVBoxLayout()
        v1.setSpacing(4)
        start_lbl = QLabel("Start Time")
        start_lbl.setStyleSheet("font-size: 11px; color: #475569;")
        v1.addWidget(start_lbl)
        self.create_start = QDateTimeEdit(QDateTime.currentDateTime())
        self.create_start.setFixedHeight(38)
        v1.addWidget(self.create_start)
        date_row.addLayout(v1)

        v2 = QVBoxLayout()
        v2.setSpacing(4)
        end_lbl = QLabel("End Time")
        end_lbl.setStyleSheet("font-size: 11px; color: #475569;")
        v2.addWidget(end_lbl)
        self.create_end = QDateTimeEdit(QDateTime.currentDateTime().addDays(7))
        self.create_end.setFixedHeight(38)
        v2.addWidget(self.create_end)
        date_row.addLayout(v2)

        layout.addLayout(date_row)

        # Options
        options_label = QLabel("OPTIONS")
        options_label.setObjectName("SectionHeader")
        layout.addWidget(options_label)

        options = QHBoxLayout()
        options.setSpacing(16)

        v3 = QVBoxLayout()
        v3.setSpacing(4)
        max_lbl = QLabel("Max Users (0 = unlimited)")
        max_lbl.setStyleSheet("font-size: 11px; color: #475569;")
        v3.addWidget(max_lbl)
        self.create_max = QSpinBox()
        self.create_max.setFixedHeight(38)
        v3.addWidget(self.create_max)
        options.addLayout(v3)

        self.create_public = QCheckBox("Public Competition")
        self.create_public.setChecked(True)
        options.addWidget(self.create_public, alignment=Qt.AlignBottom)
        layout.addLayout(options)

        # Focus Apps (optional)
        fa_label = QLabel("FOCUS APPS (OPTIONAL)")
        fa_label.setObjectName("SectionHeader")
        layout.addWidget(fa_label)

        fa_desc = QLabel("Specify required apps. Leave empty for a general competition.")
        fa_desc.setStyleSheet("color: #334155; font-size: 11px;")
        fa_desc.setWordWrap(True)
        layout.addWidget(fa_desc)

        fa_row = QHBoxLayout()
        self.focus_app_input = QLineEdit()
        self.focus_app_input.setPlaceholderText("e.g. 'code.exe' or 'chrome.exe'")
        self.focus_app_input.setFixedHeight(38)
        fa_row.addWidget(self.focus_app_input)
        add_fa_btn = QPushButton("+ Add")
        add_fa_btn.setProperty("theme", "primary")
        add_fa_btn.setFixedWidth(80)
        add_fa_btn.setFixedHeight(38)
        add_fa_btn.setCursor(Qt.PointingHandCursor)
        add_fa_btn.clicked.connect(self._add_focus_app)
        fa_row.addWidget(add_fa_btn)
        layout.addLayout(fa_row)

        self.focus_apps_list = QListWidget()
        self.focus_apps_list.setMaximumHeight(80)
        layout.addWidget(self.focus_apps_list)

        # Create button
        create_btn = QPushButton("Create Competition")
        create_btn.setProperty("theme", "success")
        create_btn.setFixedHeight(46)
        create_btn.setCursor(Qt.PointingHandCursor)
        create_btn.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                font-weight: 700;
                border-radius: 12px;
                letter-spacing: 0.5px;
            }
        """)
        create_btn.clicked.connect(self._create_competition)
        layout.addWidget(create_btn)
        layout.addStretch()

        scroll.setWidget(widget)
        return scroll

    def _add_focus_app(self):
        text = self.focus_app_input.text().strip()
        if text:
            item = QListWidgetItem(text)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Checked)
            self.focus_apps_list.addItem(item)
            self.focus_app_input.clear()

    def _create_competition(self):
        name = self.create_name.text().strip()
        if not name: return
        start = self.create_start.dateTime().toString("yyyy-MM-dd HH:mm:ss")
        end = self.create_end.dateTime().toString("yyyy-MM-dd HH:mm:ss")

        # Collect focus apps
        focus_apps = []
        for i in range(self.focus_apps_list.count()):
            item = self.focus_apps_list.item(i)
            if item.checkState() == Qt.Checked:
                focus_apps.append(item.text())

        response = self.network_client.create_competition(
            name=name, start_date=start, end_date=end,
            description=self.create_desc.toPlainText().strip(),
            max_participants=self.create_max.value(),
            is_public=self.create_public.isChecked(),
            focus_apps=focus_apps if focus_apps else None
        )
        if response.get("status") == "success":
            self._load_my_rooms()
            self.sub_tabs.setCurrentIndex(0)

    def _build_join_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(44, 44, 44, 44)
        layout.setSpacing(20)

        header = QLabel("JOIN BY CODE")
        header.setObjectName("SectionHeader")
        layout.addWidget(header)

        desc = QLabel("Enter the room code shared by the competition host.")
        desc.setStyleSheet("color: #475569; font-size: 13px; margin-bottom: 8px;")
        layout.addWidget(desc)

        self.join_code_input = QLineEdit()
        self.join_code_input.setPlaceholderText("Room code...")
        self.join_code_input.setFixedHeight(46)
        layout.addWidget(self.join_code_input)

        join_btn = QPushButton("Join Room")
        join_btn.setProperty("theme", "primary")
        join_btn.setFixedHeight(46)
        join_btn.setCursor(Qt.PointingHandCursor)
        join_btn.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                font-weight: 700;
                border-radius: 12px;
            }
        """)
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
