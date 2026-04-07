from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt

class SettingsTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        
        label = QLabel("⚙️ Settings\n\n(Under Construction)")
        label.setStyleSheet("font-size: 24px; color: #B9BBBE; font-weight: bold;")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        
        self.setLayout(layout)