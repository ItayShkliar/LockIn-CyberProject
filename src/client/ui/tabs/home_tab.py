from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame

class HomeTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 40, 40, 40)
        
        title = QLabel("Dashboard & Social")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: white;")
        layout.addWidget(title)
        
        # Daily Stats Card
        daily_card = QFrame()
        daily_card.setStyleSheet("background-color: #202225; border-radius: 10px; padding: 20px;")
        daily_layout = QVBoxLayout(daily_card)
        daily_layout.addWidget(QLabel("<h2 style='color: #43B581;'>Today's Focus</h2>"))
        self.daily_time_label = QLabel("<h1 style='color: white;'>00:00:00</h1>")
        daily_layout.addWidget(self.daily_time_label)
        layout.addWidget(daily_card)
        
        # Placeholders for Competitions
        comps_card = QFrame()
        comps_card.setStyleSheet("background-color: #202225; border-radius: 10px; padding: 20px; margin-top: 20px;")
        comps_layout = QVBoxLayout(comps_card)
        comps_layout.addWidget(QLabel("<h2 style='color: #FAA61A;'>Active Competitions & Groups</h2>"))
        comps_layout.addWidget(QLabel("<p style='color: #B9BBBE;'>[Feature coming soon: Live leaderboards will appear here]</p>"))
        layout.addWidget(comps_card)
        
        layout.addStretch()
        self.setLayout(layout)