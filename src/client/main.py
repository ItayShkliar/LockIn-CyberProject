"""
Client Application Entry Point
Manages the main window and navigation between different views.
"""
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QStackedWidget, QMessageBox
from PyQt5.QtCore import QTimer

from ui.login_view import LoginView
from ui.dashboard_view import DashboardView
from ui.settings_view import SettingsView
from logic.session_manager import SessionManager

class LockInApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Lock In - Focus App")
        self.setFixedSize(800, 600)
        
        self.apps_to_block = []
        
        # Replace AppMonitor with our new SessionManager
        self._session_manager = SessionManager() 
        
        # Create a timer to update the dashboard live
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
        
        self._login_view._login_btn.clicked.connect(self._handle_login)
        self._dashboard_view._settings_btn.clicked.connect(self._go_to_settings)
        self._settings_view._save_btn.clicked.connect(self._save_settings_and_return)
        self._dashboard_view._start_session_btn.clicked.connect(self._toggle_session)
        
    def _handle_login(self):
        username = self._login_view._username_input.text()
        if username:
            self._dashboard_view._welcome_label.setText(f"Welcome back, {username}!")
        self._stacked_widget.setCurrentIndex(1)
        
    def _go_to_settings(self):
        self._stacked_widget.setCurrentIndex(2)
        
    def _save_settings_and_return(self):
        self.apps_to_block = self._settings_view.get_selected_apps()
        print(f"[Main] Saved apps to block: {self.apps_to_block}")
        self._stacked_widget.setCurrentIndex(1)

    def _toggle_session(self):
        if not self._session_manager.is_active:
            if not self.apps_to_block:
                QMessageBox.warning(self, "No Apps Selected", "Please select at least one app in Settings!")
                return
            
            # Start the manager and the UI timer
            self._session_manager.start_session(self.apps_to_block)
            self._timer.start(1000) # Trigger _update_live_stats every 1000 milliseconds
            
            self._dashboard_view._start_session_btn.setText("Stop Session")
            self._dashboard_view._start_session_btn.setStyleSheet("""
                QPushButton { background-color: #95A5A6; color: white; font-size: 20px; font-weight: bold; border-radius: 10px; }
                QPushButton:hover { background-color: #7F8C8D; }
            """)
            self._dashboard_view._settings_btn.setEnabled(False)
            
        else:
            # Stop the manager and the timer
            stats = self._session_manager.stop_session()
            self._timer.stop()
            
            self._dashboard_view._start_session_btn.setText("Lock In! (Start Session)")
            self._dashboard_view._start_session_btn.setStyleSheet("""
                QPushButton { background-color: #E74C3C; color: white; font-size: 20px; font-weight: bold; border-radius: 10px; }
                QPushButton:hover { background-color: #C0392B; }
            """)
            self._dashboard_view._settings_btn.setEnabled(True) 
            
            QMessageBox.information(
                self, "Session Ended", 
                f"Session complete!\nTime: {stats['time_seconds']} sec\nDistractions: {stats['distractions']}\nFinal Score: {stats['final_score']}"
            )

    def _update_live_stats(self):
        """Fetches current stats from the manager and updates the Dashboard UI."""
        elapsed, dists, score = self._session_manager.get_current_stats()
        
        # Format seconds into HH:MM:SS
        mins, secs = divmod(elapsed, 60)
        hours, mins = divmod(mins, 60)
        time_str = f"{hours:02d}:{mins:02d}:{secs:02d}"
        
        # Send the strings to the dashboard view
        self._dashboard_view.update_stats(time_str, str(score), str(dists))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LockInApp()
    window.show()
    sys.exit(app.exec_())