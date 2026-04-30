"""
Stats Tab — Session history with year filtering and detail popups.
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QTableWidget, QPushButton, QTableWidgetItem,
                             QHeaderView, QComboBox, QMessageBox)
from PyQt5.QtCore import Qt
from datetime import datetime

class StatsTab(QWidget):
    def __init__(self, network_client):
        super().__init__()
        self.network_client = network_client
        self.all_sessions = []
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(44, 44, 44, 44)
        layout.setSpacing(24)

        title = QLabel("Session History")
        title.setObjectName("Title")
        layout.addWidget(title)

        subtitle = QLabel("Review your past focus sessions. Click any row for details.")
        subtitle.setStyleSheet("color: #475569; font-size: 13px; margin-bottom: 4px;")
        layout.addWidget(subtitle)

        # Controls row
        header = QHBoxLayout()
        header.setSpacing(12)

        # Year Filter
        filter_label = QLabel("Filter:")
        filter_label.setStyleSheet("color: #475569; font-size: 12px; font-weight: 600;")
        header.addWidget(filter_label)

        self.year_filter = QComboBox()
        self.year_filter.addItems(["All Time", "2024", "2025", "2026", "2027"])
        self.year_filter.setFixedHeight(34)
        self.year_filter.setFixedWidth(120)
        self.year_filter.currentTextChanged.connect(self._render_sessions)
        header.addWidget(self.year_filter)

        header.addStretch()

        self.refresh_btn = QPushButton("↻  Refresh")
        self.refresh_btn.setProperty("theme", "primary")
        self.refresh_btn.setFixedSize(110, 34)
        self.refresh_btn.setCursor(Qt.PointingHandCursor)
        self.refresh_btn.clicked.connect(self.load_sessions)
        header.addWidget(self.refresh_btn)

        layout.addLayout(header)

        self.history_table = QTableWidget()
        self.history_table.setColumnCount(6)
        self.history_table.setHorizontalHeaderLabels(
            ["Start Time", "End Time", "Duration", "Focus Time", "Dists", "Task"]
        )
        self.history_table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.history_table.horizontalHeader().setStretchLastSection(True)
        self.history_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.history_table.verticalHeader().setDefaultSectionSize(44)

        # Connect click event for detailed popup
        self.history_table.cellDoubleClicked.connect(self._show_session_details)
        self.history_table.cellClicked.connect(self._show_session_details)

        layout.addWidget(self.history_table)

    def load_sessions(self):
        if not self.network_client or not self.network_client.logged_in_user_id:
            return

        self.refresh_btn.setText("Loading...")
        response = self.network_client.get_sessions(self.network_client.logged_in_user_id)

        if response.get("status") == "success":
            self.all_sessions = response.get("sessions", [])
            self._render_sessions()

        self.refresh_btn.setText("↻  Refresh")

    def _render_sessions(self):
        year_filter = self.year_filter.currentText()
        filtered_sessions = []

        # Filter sessions
        for session in self.all_sessions:
            if year_filter == "All Time":
                filtered_sessions.append(session)
            else:
                try:
                    start_dt = datetime.fromisoformat(session.get("start_time", ""))
                    if str(start_dt.year) == year_filter:
                        filtered_sessions.append(session)
                except Exception:
                    pass

        self.history_table.setRowCount(len(filtered_sessions))
        # Store a mapping of row to session so we can retrieve full stats on click
        self._row_to_session = {}

        for row, session in enumerate(filtered_sessions):
            self._row_to_session[row] = session
            try:
                start_dt = datetime.fromisoformat(session.get("start_time", ""))
                end_dt = datetime.fromisoformat(session.get("end_time", ""))

                # Showing full date and time as requested
                st_str = start_dt.strftime("%m/%d/%Y %H:%M:%S")
                et_str = end_dt.strftime("%m/%d/%Y %H:%M:%S")

                total_sec = int((end_dt - start_dt).total_seconds())
                th, tr = divmod(total_sec, 3600)
                tm, ts = divmod(tr, 60)
                dur_str = f"{th:02d}:{tm:02d}:{ts:02d}"

                focus_sec = session.get("focus_time_seconds", 0)
                fh, fr = divmod(focus_sec, 3600)
                fm, fs = divmod(fr, 60)
                foc_str = f"{fh:02d}:{fm:02d}:{fs:02d}"

                self.history_table.setItem(row, 0, QTableWidgetItem(st_str))
                self.history_table.setItem(row, 1, QTableWidgetItem(et_str))
                self.history_table.setItem(row, 2, QTableWidgetItem(dur_str))
                self.history_table.setItem(row, 3, QTableWidgetItem(foc_str))
                self.history_table.setItem(row, 4, QTableWidgetItem(str(session.get("distraction_count", 0))))
                self.history_table.setItem(row, 5, QTableWidgetItem(session.get("description", "")))
            except Exception as e:
                print(f"Error formatting session: {e}")

        # Ensure full strings are visible
        self.history_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.history_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.history_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.history_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.history_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.history_table.horizontalHeader().setSectionResizeMode(5, QHeaderView.Stretch)

    def _show_session_details(self, row, col):
        session = getattr(self, "_row_to_session", {}).get(row)
        if not session:
            return

        try:
            start_dt = datetime.fromisoformat(session.get("start_time", ""))
            end_dt = datetime.fromisoformat(session.get("end_time", ""))

            st_str = start_dt.strftime("%B %d, %Y - %H:%M:%S")
            et_str = end_dt.strftime("%B %d, %Y - %H:%M:%S")

            total_sec = int((end_dt - start_dt).total_seconds())
            focus_sec = session.get("focus_time_seconds", 0)
            dists = session.get("distraction_count", 0)

            # Use the shared stats engine to calculate the score accurately
            import sys
            import os
            src_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
            if src_dir not in sys.path:
                sys.path.append(src_dir)
            from server.logic.stats_engine import StatsEngine

            score = StatsEngine.calculate_focus_score(focus_sec, total_sec, dists)

            task = session.get("description", "Focus Session")

            msg = (
                f"Task: {task}\n\n"
                f"Start: {st_str}\n"
                f"End:   {et_str}\n\n"
                f"Total Duration: {total_sec} seconds\n"
                f"Total Focus Time: {focus_sec} seconds\n"
                f"Distractions: {dists}\n\n"
                f"Calculated Score: {score}/100"
            )
            QMessageBox.information(self, "Session Details", msg)
        except Exception:
            pass