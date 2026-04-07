from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableWidget

class StatsTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 40, 40, 40)
        
        title = QLabel("All-Time Statistics")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: white; margin-bottom: 20px;")
        layout.addWidget(title)
        
        # Placeholder for dynamic table
        self.history_table = QTableWidget()
        self.history_table.setStyleSheet("background-color: #202225; color: white; border: none; border-radius: 5px;")
        layout.addWidget(self.history_table)
        
        self.setLayout(layout)