import sys
import datetime
from PyQt5.QtWidgets import QApplication, QMainWindow, QStackedWidget, QMessageBox
from PyQt5.QtCore import QTimer

from ui.login_view import LoginView
from ui.dashboard_view import DashboardView
from ui.settings_view import SettingsView
from logic.session_manager import SessionManager
from logic.config_manager import ConfigManager
from logic.network_client import NetworkClient # <-- NEW IMPORT

class LockInApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Lock In - Focus App")
        self.setFixedSize(800, 600)
        
        self._config_manager = ConfigManager()
        saved_data = self._config_manager.load_config()
        self.apps_to_block = saved_data.get("blocked_apps", [])
        
        self._session_manager = SessionManager() 
        self._network_client = NetworkClient() # <-- INITIALIZE NETWORK CLIENT
        
        self._timer = QTimer()
        self._timer.timeout.connect(self._update_live_stats)
        
        self._stacked_widget = QStackedWidget()
        self.setCentralWidget(self._stacked_widget)
        
        self._login_view = LoginView()
        self._dashboard_view = DashboardView()
        self._settings_view = SettingsView()
        
        self._stacked_widget.addWidget(self._login_view)     
        self._stacked_widget.addWidget(self._dashboard_view) 
        self._stacked_widget.addWidget(self._settings_view)  
        
        # Connect Login/Register Buttons
        self._login_view._login_btn.clicked.connect(self._handle_login)
        self._login_view._register_btn.clicked.connect(self._handle_register) # <-- NEW
        
        self._dashboard_view._settings_btn.clicked.connect(self._go_to_settings)
        self._settings_view._save_btn.clicked.connect(self._save_settings_and_return)
        self._dashboard_view._start_session_btn.clicked.connect(self._toggle_session)
        
    def _handle_login(self):
        """Attempts to log the user in via the server."""
        username = self._login_view._username_input.text()
        password = self._login_view._password_input.text()
        
        if not username or not password:
            QMessageBox.warning(self, "Error", "Please enter both username and password!")
            return
            
        # Call the server
        response = self._network_client.login(username, password)
        
        if response.get("status") == "success":
            self._dashboard_view._welcome_label.setText(f"Welcome back, {username}!")
            self._stacked_widget.setCurrentIndex(1) # Go to Dashboard
        else:
            QMessageBox.critical(self, "Login Failed", response.get("message", "Unknown error occurred"))

    def _handle_register(self):
        """Attempts to register a new user via the server."""
        username = self._login_view._username_input.text()
        password = self._login_view._password_input.text()
        email = self._login_view._email_input.text()
        
        if not username or not password or not email:
            QMessageBox.warning(self, "Error", "Please enter username, email, and password to register!")
            return
            
        # Call the server
        response = self._network_client.register(username, email, password)
        
        if response.get("status") == "success":
            QMessageBox.information(self, "Success", "Registration successful! You can now log in.")
            self._login_view._email_input.clear() # Clear email so they can log in
        else:
            QMessageBox.critical(self, "Registration Failed", response.get("message", "Unknown error occurred"))

    # ... (Keep all the remaining methods _go_to_settings, _save_settings_and_return, _toggle_session, _update_live_stats exactly as they were) ...
    def _go_to_settings(self):
        self._stacked_widget.setCurrentIndex(2)
        
    def _save_settings_and_return(self):
        self.apps_to_block = self._settings_view.get_selected_apps()
        self._config_manager.save_config({"blocked_apps": self.apps_to_block})
        self._stacked_widget.setCurrentIndex(1)

    def _toggle_session(self):
        if not self._session_manager.is_active:
            if not self.apps_to_block: # (This is now your Focus Apps list!)
                QMessageBox.warning(self, "No Apps Selected", "Please select the apps you want to focus on in Settings!")
                return
            self._session_manager.start_session(self.apps_to_block)
            self._timer.start(1000) 
            self._dashboard_view._start_session_btn.setText("Stop Session")
            self._dashboard_view._start_session_btn.setStyleSheet("QPushButton { background-color: #95A5A6; color: white; font-size: 20px; font-weight: bold; border-radius: 10px; } QPushButton:hover { background-color: #7F8C8D; }")
            self._dashboard_view._settings_btn.setEnabled(False)
        else:
            # STOPPING THE SESSION
            stats = self._session_manager.stop_session()
            self._timer.stop()
            
            end_time = datetime.datetime.now()
            start_time = end_time - datetime.timedelta(seconds=stats['total_time_seconds'])
            
            session_data = {
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "focus_time_seconds": stats['focus_time_seconds'], # <--- NOW UPLOADING REAL FOCUS TIME
                "distraction_count": stats['distractions'],
                "description": "Desktop Focus Session",
                "status": "completed"
            }
            
            if self._network_client.logged_in_user_id:
                response = self._network_client.upload_session(session_data)
                if response.get("status") == "success":
                    print(f"[Main] Session successfully uploaded to database! ID: {response.get('session_id')}")
            
            self._dashboard_view._start_session_btn.setText("Lock In! (Start Session)")
            self._dashboard_view._start_session_btn.setStyleSheet("QPushButton { background-color: #E74C3C; color: white; font-size: 20px; font-weight: bold; border-radius: 10px; } QPushButton:hover { background-color: #C0392B; }")
            self._dashboard_view._settings_btn.setEnabled(True) 
            
            QMessageBox.information(self, "Session Ended", f"Total Time: {stats['total_time_seconds']}s\nActual Focus Time: {stats['focus_time_seconds']}s\nDistractions: {stats['distractions']}\nFinal Score: {stats['final_score']}")

    def _update_live_stats(self):
        total, focus, dists, score = self._session_manager.get_current_stats()
        mins, secs = divmod(total, 60)
        hours, mins = divmod(mins, 60)
        time_str = f"{hours:02d}:{mins:02d}:{secs:02d}"
        
        # We can update the dashboard to show Focus Time vs Total Time later if you want!
        self._dashboard_view.update_stats(time_str, str(score), str(dists))
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LockInApp()
    window.show()
    sys.exit(app.exec_())