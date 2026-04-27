from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QStackedWidget, QLabel
from PyQt5.QtCore import Qt

class MainWindowView(QWidget):
    def __init__(self):
        super().__init__()
        self._init_ui()

    def _init_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 1. SIDEBAR
        sidebar = QWidget()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(240)
        
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(15, 30, 15, 30)
        sidebar_layout.setSpacing(8)

        logo = QLabel("Lock In")
        logo.setObjectName("Logo")
        logo.setAlignment(Qt.AlignCenter)
        sidebar_layout.addWidget(logo)
        sidebar_layout.addSpacing(20)

        # Navigation Buttons
        self.nav_buttons = {}
        nav_items = [
            ("home_btn", "🏠 Home"),
            ("focus_btn", "⏱️ Focus"),            
            ("competitions_btn", "🏆 Competitions"),
            ("leaderboard_btn", "📊 Leaderboards"),
            ("stats_btn", "📈 All-Time Stats"),
            ("settings_btn", "⚙️ Settings")
        ]

        for btn_name, text in nav_items:
            btn = QPushButton(text)
            btn.setObjectName("NavBtn")
            btn.setFixedHeight(50)
            btn.setCursor(Qt.PointingHandCursor)
            self.nav_buttons[btn_name] = btn
            sidebar_layout.addWidget(btn)

        sidebar_layout.addStretch()

        # Logout Button
        self.logout_btn = QPushButton("🚪 Logout")
        self.logout_btn.setObjectName("LogoutBtn") # I'll add specific style for this in style.py or use danger
        self.logout_btn.setProperty("theme", "danger")
        self.logout_btn.setFixedHeight(45)
        sidebar_layout.addWidget(self.logout_btn)

        # 2. CONTENT AREA
        self.content_area = QStackedWidget()
        self.content_area.setObjectName("ContentArea")

        main_layout.addWidget(sidebar)
        main_layout.addWidget(self.content_area)

    def add_tab(self, widget: QWidget):
        self.content_area.addWidget(widget)

    def switch_tab(self, index: int):
        # Update active state for buttons
        for i, btn in enumerate(self.nav_buttons.values()):
            btn.setProperty("active", i == index)
            btn.style().unpolish(btn)
            btn.style().polish(btn)
        
        self.content_area.setCurrentIndex(index)