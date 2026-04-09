from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QComboBox, QPushButton, QDateTimeEdit, QMessageBox, QFrame)
from PyQt5.QtCore import Qt, QDateTime
from datetime import datetime, timedelta

class CompetitionsTab(QWidget):
    def __init__(self, network_client):
        super().__init__()
        self.network_client = network_client
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)

        title = QLabel("🏆 Competitions")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: white;")
        layout.addWidget(title)

        # ==========================================
        # SECTION 1: JOIN A COMPETITION
        # ==========================================
        join_card = QFrame()
        join_card.setStyleSheet("background-color: #202225; border-radius: 10px; padding: 20px;")
        join_layout = QVBoxLayout(join_card)

        join_title = QLabel("Join Existing Room")
        join_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #43B581;")
        
        join_input_layout = QHBoxLayout()
        self.join_input = QLineEdit()
        self.join_input.setPlaceholderText("Enter Room Code...")
        self.join_input.setStyleSheet("background-color: #2F3136; color: white; padding: 10px; border-radius: 5px;")
        
        self.join_btn = QPushButton("Join")
        self.join_btn.setFixedSize(100, 40)
        self.join_btn.setStyleSheet("background-color: #43B581; color: white; font-weight: bold; border-radius: 5px;")
        self.join_btn.clicked.connect(self.handle_join)

        join_input_layout.addWidget(self.join_input)
        join_input_layout.addWidget(self.join_btn)

        join_layout.addWidget(join_title)
        join_layout.addLayout(join_input_layout)
        layout.addWidget(join_card)

        # ==========================================
        # SECTION 2: CREATE A COMPETITION
        # ==========================================
        create_card = QFrame()
        create_card.setStyleSheet("background-color: #202225; border-radius: 10px; padding: 20px;")
        create_layout = QVBoxLayout(create_card)

        create_title = QLabel("Create New Room")
        create_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #7289DA;")
        create_layout.addWidget(create_title)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Room Name (e.g., Weekend Grind)")
        self.name_input.setStyleSheet("background-color: #2F3136; color: white; padding: 10px; border-radius: 5px;")
        create_layout.addWidget(self.name_input)

        self.desc_input = QLineEdit()
        self.desc_input.setPlaceholderText("Optional description...")
        self.desc_input.setStyleSheet("background-color: #2F3136; color: white; padding: 10px; border-radius: 5px;")
        create_layout.addWidget(self.desc_input)

        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["24 Hour Sprint", "1 Week Challenge", "Custom Dates"])
        self.mode_combo.setStyleSheet("background-color: #2F3136; color: white; padding: 5px; border-radius: 5px;")
        self.mode_combo.currentIndexChanged.connect(self.toggle_custom_dates)
        create_layout.addWidget(self.mode_combo)

        # Custom Dates (Hidden by default)
        self.custom_dates_widget = QWidget()
        cd_layout = QHBoxLayout(self.custom_dates_widget)
        cd_layout.setContentsMargins(0, 0, 0, 0)
        
        self.start_date_edit = QDateTimeEdit(QDateTime.currentDateTime())
        self.start_date_edit.setStyleSheet("background-color: #2F3136; color: white;")
        self.end_date_edit = QDateTimeEdit(QDateTime.currentDateTime().addDays(1))
        self.end_date_edit.setStyleSheet("background-color: #2F3136; color: white;")
        
        cd_layout.addWidget(QLabel("<span style='color:white;'>Start:</span>"))
        cd_layout.addWidget(self.start_date_edit)
        cd_layout.addWidget(QLabel("<span style='color:white;'>End:</span>"))
        cd_layout.addWidget(self.end_date_edit)
        
        create_layout.addWidget(self.custom_dates_widget)
        self.toggle_custom_dates()

        self.create_btn = QPushButton("Create Room")
        self.create_btn.setFixedHeight(40)
        self.create_btn.setStyleSheet("background-color: #7289DA; color: white; font-weight: bold; border-radius: 5px; margin-top: 10px;")
        self.create_btn.clicked.connect(self.handle_create)
        create_layout.addWidget(self.create_btn)

        layout.addWidget(create_card)
        layout.addStretch()
        self.setLayout(layout)

    def toggle_custom_dates(self):
        is_custom = self.mode_combo.currentText() == "Custom Dates"
        self.custom_dates_widget.setVisible(is_custom)

    def handle_join(self):
        code = self.join_input.text().strip()
        if not code.isdigit():
            QMessageBox.warning(self, "Error", "Room Code must be a number.")
            return

        response = self.network_client.join_competition(int(code))
        if response.get("status") == "success":
            QMessageBox.information(self, "Success", f"Joined room {code} successfully!")
            self.join_input.clear()
        else:
            QMessageBox.warning(self, "Error", response.get("message", "Failed to join room."))

    def handle_create(self):
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Error", "Room Name cannot be empty.")
            return

        mode = self.mode_combo.currentText()
        now = datetime.now()

        if mode == "24 Hour Sprint":
            start_str = now.strftime("%Y-%m-%d %H:%M:%S")
            end_str = (now + timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
        elif mode == "1 Week Challenge":
            start_str = now.strftime("%Y-%m-%d %H:%M:%S")
            end_str = (now + timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")
        else:
            start_str = self.start_date_edit.dateTime().toString("yyyy-MM-dd HH:mm:ss")
            end_str = self.end_date_edit.dateTime().toString("yyyy-MM-dd HH:mm:ss")

        response = self.network_client.create_competition(
            name=name,
            start_date=start_str,
            end_date=end_str,
            description=self.desc_input.text().strip()
        )

        if response.get("status") == "success":
            room_code = response.get("room_code")
            QMessageBox.information(self, "Success", f"Room Created!\n\nYour Room Code is: {room_code}")
            self.name_input.clear()
            self.desc_input.clear()
        else:
            QMessageBox.warning(self, "Error", response.get("message", "Failed to create room."))