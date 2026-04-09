from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, QPushButton, QTableWidgetItem, QHeaderView
from PyQt5.QtCore import Qt
from datetime import datetime

class StatsTab(QWidget):
    def __init__(self, network_client):
        super().__init__()
        self.network_client = network_client
        
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 40, 40, 40)
        
        # --- HEADER (Title + Refresh Button) ---
        header_layout = QHBoxLayout()
        title = QLabel("All-Time Statistics")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: white;")
        
        self.refresh_btn = QPushButton("🔄 Refresh")
        self.refresh_btn.setFixedSize(120, 40)
        self.refresh_btn.setStyleSheet("background-color: #7289DA; color: white; font-weight: bold; border-radius: 5px;")
        self.refresh_btn.clicked.connect(self.load_sessions)
        
        header_layout.addWidget(title)
        header_layout.addStretch() # Pushes the button to the right
        header_layout.addWidget(self.refresh_btn)
        
        layout.addLayout(header_layout)
        layout.addSpacing(20)
        
        # --- DYNAMIC TABLE ---
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(5) 
        self.history_table.setHorizontalHeaderLabels(["Start Time", "End Time", "Duration (s)", "Focus (s)", "Distractions", "Description"])
        
        # Modern Dark Theme Styling
        self.history_table.setStyleSheet("""
            QTableWidget {
                background-color: #202225; color: white; border: none; border-radius: 5px;
                gridline-color: #2F3136;
            }
            QHeaderView::section {
                background-color: #2F3136; color: white; font-weight: bold; border: none; padding: 8px;
            }
            QTableWidget::item { padding: 5px; }
        """)
        
        # Make columns stretch to fit the window
        self.history_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # Prevent manual editing of the cells
        self.history_table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        layout.addWidget(self.history_table)
        self.setLayout(layout)

    def load_sessions(self):
        """Fetches data from the API and populates the table."""
        if not self.network_client or not self.network_client.logged_in_user_id:
            return
            
        self.refresh_btn.setText("Loading...")
        
        response = self.network_client.get_sessions(self.network_client.logged_in_user_id)
        
        if response.get("status") == "success":
            sessions = response.get("sessions", [])
            self.history_table.setRowCount(len(sessions))
            
            for row_idx, session in enumerate(sessions):
                total_time = datetime.fromisoformat(session.get("end_time", "")) - datetime.fromisoformat(session.get("start_time", ""))
                self.history_table.setItem(row_idx, 0, QTableWidgetItem(str(session.get("start_time", ""))))
                self.history_table.setItem(row_idx, 1, QTableWidgetItem(str(session.get("end_time", ""))))
                self.history_table.setItem(row_idx, 2, QTableWidgetItem(str(total_time)))
                focus_seconds = session.get("focus_time_seconds", 0)
                self.history_table.setItem(row_idx, 3, QTableWidgetItem(str(f"{focus_seconds // 3600:02}:{(focus_seconds % 3600) // 60:02}:{focus_seconds % 60:02}")))
                self.history_table.setItem(row_idx, 4, QTableWidgetItem(str(session.get("distraction_count", 0))))
                self.history_table.setItem(row_idx, 5, QTableWidgetItem(str(session.get("description", ""))))
                
        self.refresh_btn.setText("🔄 Refresh")