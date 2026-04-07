from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QListWidget, QListWidgetItem, QHBoxLayout, QFrame, QLineEdit
from PyQt5.QtCore import Qt

class FocusTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 40, 40, 40)
        
        title = QLabel("Start a Focus Session")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: white;")
        layout.addWidget(title)
        
        # ==========================================
        # 1. SETUP MODE WIDGET (Visible by default)
        # ==========================================
        self.setup_widget = QWidget()
        setup_layout = QVBoxLayout(self.setup_widget)
        setup_layout.setContentsMargins(0, 0, 0, 0)
        
        self.desc_input = QLineEdit()
        self.desc_input.setPlaceholderText("What are you focusing on? (e.g., 'Calculus HW')")
        self.desc_input.setStyleSheet("background-color: #202225; color: white; padding: 10px; border-radius: 5px; font-size: 14px; margin-bottom: 10px;")
        
        setup_layout.addWidget(self.desc_input)
        instructions = QLabel("Select the apps you intend to work on, then Lock In.")
        instructions.setStyleSheet("color: #B9BBBE; font-size: 14px;")
        setup_layout.addWidget(instructions)
        
        self.app_list = QListWidget()
        self.app_list.setStyleSheet("background-color: #202225; color: white; border: none; border-radius: 5px; padding: 10px;")
        setup_layout.addWidget(self.app_list)
        
        self.scan_btn = QPushButton("🔄 Scan Running Apps")
        self.scan_btn.setStyleSheet("background-color: #7289DA; color: white; padding: 10px; border-radius: 5px; font-weight: bold;")
        setup_layout.addWidget(self.scan_btn)
        
        layout.addWidget(self.setup_widget)

        # ==========================================
        # 2. ACTIVE SESSION WIDGET (Hidden by default)
        # ==========================================
        self.active_widget = QWidget()
        active_layout = QVBoxLayout(self.active_widget)
        active_layout.setContentsMargins(0, 0, 0, 0)
        
        self.focus_apps_label = QLabel("🎯 Locked in on: None")
        self.focus_apps_label.setStyleSheet("color: #43B581; font-size: 18px; font-weight: bold; margin-bottom: 20px;")
        self.focus_apps_label.setAlignment(Qt.AlignCenter)
        self.focus_apps_label.setWordWrap(True)
        active_layout.addWidget(self.focus_apps_label)
        
        # We put the Distractions and Score next to each other
        stats_layout = QHBoxLayout()
        
        self.distractions_label = QLabel("👀 Distractions: 0")
        self.distractions_label.setStyleSheet("font-size: 20px; color: #E74C3C; font-weight: bold;")
        self.distractions_label.setAlignment(Qt.AlignCenter)
        
        self.score_label = QLabel("🏆 Focus Score: 100")
        self.score_label.setStyleSheet("font-size: 20px; color: #FAA61A; font-weight: bold;")
        self.score_label.setAlignment(Qt.AlignCenter)
        
        stats_layout.addWidget(self.distractions_label)
        stats_layout.addWidget(self.score_label)
        active_layout.addLayout(stats_layout)
        
        # Hide it initially
        self.active_widget.hide()
        layout.addWidget(self.active_widget)

        # ==========================================
        # 3. GLOBAL ELEMENTS (Always visible)
        # ==========================================
        layout.addStretch() # Pushes the timer and button to the bottom
        
        self.timer_label = QLabel("00:00:00")
        self.timer_label.setStyleSheet("font-size: 64px; font-weight: bold; color: white;")
        self.timer_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.timer_label)
        
        self.start_btn = QPushButton("LOCK IN")
        self.start_btn.setFixedHeight(60)
        self.start_btn.setStyleSheet("background-color: #43B581; color: white; font-size: 24px; font-weight: bold; border-radius: 10px;")
        layout.addWidget(self.start_btn)
        
        self.setLayout(layout)
        
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

    # ---> NEW METHODS FOR TOGGLING THE UI <---
    def set_active_mode(self, selected_apps: list):
        """Hides the scanner and shows the live stats."""
        self.setup_widget.hide()
        apps_text = ", ".join(selected_apps)
        self.focus_apps_label.setText(f"🎯 Locked in on:\n{apps_text}")
        self.distractions_label.setText("👀 Distractions: 0")
        self.score_label.setText("🏆 Focus Score: 100")
        self.active_widget.show()

    def get_description(self) -> str:
        """Returns the typed description, or a default string if empty."""
        text = self.desc_input.text().strip()
        return text if text else "Focus Session"
    
    def set_setup_mode(self):
        """Brings the scanner back and hides the live stats."""
        self.active_widget.hide()
        self.setup_widget.show()
        self.timer_label.setText("00:00:00")