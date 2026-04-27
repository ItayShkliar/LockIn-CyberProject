from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QListWidget, QListWidgetItem, QHBoxLayout, QFrame, QLineEdit
from PyQt5.QtCore import Qt

class FocusTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        
        title = QLabel("Lock In Mode")
        title.setObjectName("Title")
        layout.addWidget(title)
        
        # 1. SETUP MODE CARD
        self.setup_card = QFrame()
        self.setup_card.setObjectName("Card")
        setup_layout = QVBoxLayout(self.setup_card)
        setup_layout.setContentsMargins(20, 20, 20, 20)
        setup_layout.setSpacing(15)
        
        self.desc_input = QLineEdit()
        self.desc_input.setPlaceholderText("What are you focusing on? (e.g., 'Deep Work')")
        setup_layout.addWidget(self.desc_input)
        
        instruct = QLabel("Select the apps you want to track during your session:")
        instruct.setObjectName("Subtitle")
        setup_layout.addWidget(instruct)
        
        self.app_list = QListWidget()
        setup_layout.addWidget(self.app_list)
        
        self.scan_btn = QPushButton("🔄 Refresh Running Apps")
        self.scan_btn.setProperty("theme", "primary")
        setup_layout.addWidget(self.scan_btn)
        
        layout.addWidget(self.setup_card)

        # 2. ACTIVE SESSION CARD
        self.active_card = QFrame()
        self.active_card.setObjectName("Card")
        active_layout = QVBoxLayout(self.active_card)
        active_layout.setContentsMargins(20, 20, 20, 20)
        active_layout.setSpacing(20)
        
        self.focus_apps_label = QLabel("🎯 Tracking: None")
        self.focus_apps_label.setObjectName("Subtitle")
        self.focus_apps_label.setAlignment(Qt.AlignCenter)
        self.focus_apps_label.setWordWrap(True)
        active_layout.addWidget(self.focus_apps_label)
        
        stats_layout = QHBoxLayout()
        self.distractions_label = QLabel("👀 Distractions: 0")
        self.distractions_label.setStyleSheet("font-size: 20px; color: #ef4444; font-weight: bold;")
        
        self.score_label = QLabel("🏆 Focus Score: 100")
        self.score_label.setStyleSheet("font-size: 20px; color: #10b981; font-weight: bold;")
        
        stats_layout.addWidget(self.distractions_label)
        stats_layout.addStretch()
        stats_layout.addWidget(self.score_label)
        active_layout.addLayout(stats_layout)
        
        self.active_card.hide()
        layout.addWidget(self.active_card)

        # 3. GLOBAL TIMER & BUTTON
        layout.addStretch()
        
        timer_container = QFrame()
        timer_container.setObjectName("Card")
        timer_layout = QVBoxLayout(timer_container)
        
        self.timer_label = QLabel("00:00:00")
        self.timer_label.setStyleSheet("font-size: 80px; font-weight: bold; color: #3b82f6; font-family: 'Consolas', monospace;")
        self.timer_label.setAlignment(Qt.AlignCenter)
        timer_layout.addWidget(self.timer_label)
        layout.addWidget(timer_container)
        
        self.start_btn = QPushButton("LOCK IN")
        self.start_btn.setFixedHeight(60)
        self.start_btn.setProperty("theme", "success")
        self.start_btn.setStyleSheet("font-size: 24px;")
        layout.addWidget(self.start_btn)
        
    def populate_apps(self, apps_list):
        self.app_list.clear()
        for app in apps_list:
            item = QListWidgetItem(app)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Unchecked)
            self.app_list.addItem(item)

    def get_selected_apps(self) -> list:
        selected = []
        for i in range(self.app_list.count()):
            item = self.app_list.item(i)
            if item.checkState() == Qt.Checked:
                selected.append(item.text())
        return selected

    def set_active_mode(self, selected_apps: list):
        self.setup_card.hide()
        apps_text = ", ".join(selected_apps)
        self.focus_apps_label.setText(f"🎯 Tracking:\n{apps_text}")
        self.distractions_label.setText("👀 Distractions: 0")
        self.score_label.setText("🏆 Focus Score: 100")
        self.active_card.show()
        self.start_btn.setText("STOP SESSION")
        self.start_btn.setProperty("theme", "danger")
        self.start_btn.style().unpolish(self.start_btn)
        self.start_btn.style().polish(self.start_btn)

    def get_description(self) -> str:
        text = self.desc_input.text().strip()
        return text if text else "Focus Session"
    
    def update_stats(self, time_str: str, distractions: int, score: int):
        self.timer_label.setText(time_str)
        self.distractions_label.setText(f"👀 Distractions: {distractions}")
        self.score_label.setText(f"🏆 Focus Score: {score}")
        
        # Dynamic color for score
        score_color = "#10b981" if score >= 70 else "#f59e0b" if score >= 40 else "#ef4444"
        self.score_label.setStyleSheet(f"font-size: 20px; color: {score_color}; font-weight: bold;")

    def set_setup_mode(self):
        self.active_card.hide()
        self.setup_card.show()
        self.timer_label.setText("00:00:00")
        self.start_btn.setText("LOCK IN")
        self.start_btn.setProperty("theme", "success")
        self.start_btn.style().unpolish(self.start_btn)
        self.start_btn.style().polish(self.start_btn)