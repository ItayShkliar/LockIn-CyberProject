"""
Settings View Module
Displays a list of currently running applications and allows the user 
to select which ones they want to focus on during a session.
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, 
                             QPushButton, QListWidget, QListWidgetItem, QMessageBox)
from PyQt5.QtCore import Qt

# We need to import our scanner. 
# (The try-except block helps if we run this file directly for testing)
try:
    from logic.app_scanner import AppScanner
except ImportError:
    import sys
    import os
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from logic.app_scanner import AppScanner

class SettingsView(QWidget):
    """
    The UI screen where users configure their focus session settings,
    specifically choosing which apps they intend to focus on.
    """
    
    def __init__(self):
        super().__init__()
        self._scanner = AppScanner()
        self._init_ui()
        
    def _init_ui(self):
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(30, 30, 30, 30)
        
        # Title
        title_label = QLabel("Focus Settings")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #2C3E50;")
        title_label.setAlignment(Qt.AlignCenter)
        
        # Instructions (UPDATED FOR FOCUS PARADIGM)
        instruction_label = QLabel("Check the boxes next to the apps you want to FOCUS ON.\nAny other app will count as a distraction!")
        instruction_label.setStyleSheet("font-size: 14px; color: #E74C3C; font-weight: bold;")
        instruction_label.setAlignment(Qt.AlignCenter)
        
        # The scrollable list that will hold our apps
        self._app_list_widget = QListWidget()
        self._app_list_widget.setStyleSheet("font-size: 14px; padding: 5px;")
        
        # Refresh Button (to scan the PC again)
        self._refresh_btn = QPushButton("🔄 Scan for Running Apps")
        self._refresh_btn.setStyleSheet("padding: 8px; background-color: #3498DB; color: white; font-weight: bold;")
        self._refresh_btn.clicked.connect(self._populate_app_list)
        
        # Save/Back Button
        self._save_btn = QPushButton("Save & Return to Dashboard")
        self._save_btn.setStyleSheet("padding: 10px; background-color: #2ECC71; color: white; font-weight: bold;")
        # We will connect this button in main.py to handle navigation
        self._save_btn.clicked.connect(self.get_selected_apps) 
        
        # Add widgets to layout
        main_layout.addWidget(title_label)
        main_layout.addWidget(instruction_label)
        main_layout.addWidget(self._refresh_btn)
        main_layout.addWidget(self._app_list_widget)
        main_layout.addWidget(self._save_btn)
        
        self.setLayout(main_layout)
        
        # Populate the list immediately when the screen loads
        self._populate_app_list()

    def _populate_app_list(self):
        """
        Scans the PC using AppScanner and populates the QListWidget with checkboxes.
        """
        self._app_list_widget.clear() # Clear existing items
        running_apps = self._scanner.get_running_processes()
        
        if not running_apps:
            QMessageBox.warning(self, "Warning", "No applications found or access denied.")
            return

        for app in running_apps:
            # Create a list item
            item = QListWidgetItem(app)
            # Make it checkable (adds a checkbox)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            # Set it to unchecked by default
            item.setCheckState(Qt.Unchecked) 
            
            # Add to the visual list
            self._app_list_widget.addItem(item)
            
        print(f"[UI] Populated list with {len(running_apps)} apps.")

    def get_selected_apps(self) -> list:
        """
        Iterates through the list and returns the names of the apps 
        that the user has checked.
        """
        selected_apps = []
        for index in range(self._app_list_widget.count()):
            item = self._app_list_widget.item(index)
            if item.checkState() == Qt.Checked:
                selected_apps.append(item.text())
                
        print(f"[UI] User selected the following FOCUS apps: {selected_apps}")
        return selected_apps

# ==========================================
# Test Execution Block
# ==========================================
if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = SettingsView()
    window.setWindowTitle("Test Settings View")
    window.resize(400, 500)
    window.show()
    sys.exit(app.exec_())