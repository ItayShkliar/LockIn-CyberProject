"""
Main Window View Module (The Shell)
Handles the modern sidebar navigation and the dynamic content area.
"""
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QStackedWidget, QLabel
from PyQt5.QtCore import Qt

class MainWindowView(QWidget):
    def __init__(self):
        super().__init__()
        self._init_ui()

    def _init_ui(self):
        # The main layout is Horizontal (Sidebar on left, Content on right)
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0) # Remove default borders
        main_layout.setSpacing(0)

        # ==========================================
        # 1. SIDEBAR SETUP (Left Side)
        # ==========================================
        sidebar = QWidget()
        sidebar.setFixedWidth(220)
        sidebar.setStyleSheet("background-color: #2F3136; color: white;") # Discord-like dark theme
        
        sidebar_layout = QVBoxLayout()
        sidebar_layout.setContentsMargins(15, 30, 15, 30)
        sidebar_layout.setSpacing(15)

        # App Logo / Title
        logo = QLabel("Lock In")
        logo.setStyleSheet("font-size: 24px; font-weight: bold; color: #FFFFFF; margin-bottom: 20px;")
        logo.setAlignment(Qt.AlignCenter)
        sidebar_layout.addWidget(logo)

        # Navigation Buttons
        self.nav_buttons = {}
        nav_items = [
            ("home_btn", "🏠 Home"),
            ("focus_btn", "⏱️ Focus"),            
            ("competitions_btn", "🏆 Competitions"), # <-- NEW
            ("leaderboard_btn", "📊 Leaderboards"),  # <-- NEW
            ("stats_btn", "📈 All-Time Stats"),
            ("settings_btn", "⚙️ Settings")
        ]

        for btn_name, text in nav_items:
            btn = QPushButton(text)
            btn.setFixedHeight(45)
            # Modern flat button styling with hover effect
            btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: #B9BBBE;
                    font-size: 16px;
                    font-weight: bold;
                    text-align: left;
                    padding-left: 15px;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: #393C43;
                    color: white;
                }
            """)
            self.nav_buttons[btn_name] = btn
            sidebar_layout.addWidget(btn)

        sidebar_layout.addStretch() # Pushes everything above to the top

        # Logout Button at the bottom
        self.logout_btn = QPushButton("🚪 Logout")
        self.logout_btn.setFixedHeight(45)
        self.logout_btn.setStyleSheet("background-color: #E74C3C; color: white; font-size: 14px; font-weight: bold; border-radius: 5px;")
        sidebar_layout.addWidget(self.logout_btn)

        sidebar.setLayout(sidebar_layout)

        # ==========================================
        # 2. CONTENT AREA SETUP (Right Side)
        # ==========================================
        self.content_area = QStackedWidget()
        self.content_area.setStyleSheet("background-color: #36393F;") # Slightly lighter dark theme for content

        # Add parts to main layout
        main_layout.addWidget(sidebar)
        main_layout.addWidget(self.content_area)
        self.setLayout(main_layout)

    def add_tab(self, widget: QWidget):
        """Adds a new tab view into the content area."""
        self.content_area.addWidget(widget)

    def switch_tab(self, index: int):
        """Changes the currently displayed tab."""
        self.content_area.setCurrentIndex(index)