"""
Main Application Entry Point
Orchestrates the UI views and Logic managers.
"""
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QStackedWidget, QMessageBox
from PyQt5.QtCore import QTimer 

# Import UI Views
from ui.login_view import LoginView
from ui.main_window_view import MainWindowView
from ui.tabs.home_tab import HomeTab
from ui.tabs.focus_tab import FocusTab
from ui.tabs.competitions_tab import CompetitionsTab # <-- NEW
from ui.tabs.leaderboard_tab import LeaderboardTab   # <-- NEW
from ui.tabs.stats_tab import StatsTab
from ui.tabs.settings_tab import SettingsTab
from ui.style import GLOBAL_STYLESHEET

# Import Logic Managers
from logic.network_client import NetworkClient
from logic.session_manager import SessionManager

class LockInApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Lock In - Productivity")
        self.resize(1000, 700) 
        # Application context stylesheet is set in __main__ or globally via QApplication
        
        self.network_client = NetworkClient()
        self.session_manager = SessionManager()
        
        # Setup the UI Timer
        self.session_timer = QTimer()
        self.session_timer.timeout.connect(self.update_timer_ui)
        
        self.main_stack = QStackedWidget()
        self.setCentralWidget(self.main_stack)
        
        self.login_view = LoginView()
        self.main_window = MainWindowView()
        
        self.main_stack.addWidget(self.login_view)
        self.main_stack.addWidget(self.main_window)
        
        self._setup_tabs()
        self._connect_signals()

    def _setup_tabs(self):
        self.home_tab = HomeTab(self.network_client)
        self.focus_tab = FocusTab()
        self.comps_tab = CompetitionsTab(self.network_client)       # <-- NEW
        self.leaderboard_tab = LeaderboardTab(self.network_client)  # <-- NEW
        self.stats_tab = StatsTab(self.network_client)
        self.settings_tab = SettingsTab(self.network_client)
        
        self.main_window.add_tab(self.home_tab)          # Index 0
        self.main_window.add_tab(self.focus_tab)         # Index 1
        self.main_window.add_tab(self.comps_tab)         # Index 2 <-- NEW
        self.main_window.add_tab(self.leaderboard_tab)   # Index 3 <-- NEW
        self.main_window.add_tab(self.stats_tab)         # Index 4
        self.main_window.add_tab(self.settings_tab)      # Index 5

    def _connect_signals(self):
        self.login_view._login_btn.clicked.connect(self.handle_login)
        self.login_view._register_btn.clicked.connect(self.handle_register)
        
        # Wire up the sidebar navigation!
        self.main_window.nav_buttons["home_btn"].clicked.connect(lambda: self.main_window.switch_tab(0))
        self.main_window.nav_buttons["focus_btn"].clicked.connect(lambda: self.main_window.switch_tab(1))
        self.main_window.nav_buttons["competitions_btn"].clicked.connect(lambda: self.main_window.switch_tab(2)) # <-- NEW
        self.main_window.nav_buttons["leaderboard_btn"].clicked.connect(lambda: self.main_window.switch_tab(3))  # <-- NEW
        self.main_window.nav_buttons["stats_btn"].clicked.connect(lambda: self.main_window.switch_tab(4))
        self.main_window.nav_buttons["settings_btn"].clicked.connect(lambda: self.main_window.switch_tab(5))
        
        self.main_window.logout_btn.clicked.connect(self.handle_logout)
        
        self.focus_tab.scan_btn.clicked.connect(self.scan_and_populate_apps)
        self.focus_tab.scan_tabs_btn.clicked.connect(self.scan_browser_tabs)
        self.focus_tab.start_btn.clicked.connect(self.toggle_session)

    # ==========================================
    # Action Handlers
    # ==========================================
    def handle_login(self):
        """Grabs input from UI and logs into the Socket Server."""
        username = self.login_view._username_input.text()
        password = self.login_view._password_input.text()
        
        if not username or not password:
            QMessageBox.warning(self, "Error", "Please enter both username and password.")
            return
            
        response = self.network_client.login(username, password)
        
        if response.get("status") == "success":
            self.main_stack.setCurrentWidget(self.main_window)
            from PyQt5.QtCore import QTimer
            QTimer.singleShot(1000, self.network_client.sync_offline_sessions)
            self.stats_tab.load_sessions()
        else:
            QMessageBox.critical(self, "Login Failed", response.get("message", "Connection error. Is the server running?"))

    def handle_register(self):
        """Registers a new user in the Database via Socket Server."""
        username = self.login_view._username_input.text()
        email = self.login_view._email_input.text()
        password = self.login_view._password_input.text()
        
        if not username or not email or not password:
            QMessageBox.warning(self, "Error", "Please fill in all fields.")
            return
            
        response = self.network_client.register(username, email, password)
        
        if response.get("status") == "success":
            QMessageBox.information(self, "Success", "Registration successful! You can now log in.")
            self.login_view._toggle_mode()
        else:
            QMessageBox.critical(self, "Registration Failed", response.get("message", "Connection error. Is the server running?"))

    def handle_logout(self):
        self.network_client.logout()
        self.main_stack.setCurrentWidget(self.login_view)

    def scan_and_populate_apps(self):
        self.focus_tab.scan_btn.setText("Scanning...")
        QApplication.processEvents() 
        try:
            apps_list = self.session_manager.get_available_apps()
            self.focus_tab.populate_apps(apps_list)
        except Exception as e:
            print(f"[Error] Failed to scan apps: {e}")
        finally:
            self.focus_tab.scan_btn.setText("🔄 Refresh Running Apps")

    def scan_browser_tabs(self):
        """Scans open browser tabs and populates the tab list in the Focus UI."""
        self.focus_tab.scan_tabs_btn.setText("Scanning...")
        QApplication.processEvents()
        try:
            tabs = self.session_manager.get_browser_tabs()
            self.focus_tab.populate_browser_tabs(tabs)
        except Exception as e:
            print(f"[Error] Failed to scan browser tabs: {e}")
        finally:
            self.focus_tab.scan_tabs_btn.setText("🔍 Scan Open Browser Tabs")

    def toggle_session(self):
        if not self.session_manager.is_active:
            # 1. Gather Input
            selected_apps = self.focus_tab.get_selected_apps()
            if not selected_apps:
                QMessageBox.warning(self, "Hold Up", "Please select at least one app to focus on!")
                return
            
            # 2. Gather browser tab keywords (optional)
            focus_tabs = self.focus_tab.get_focus_tab_keywords()
            
            # 3. Logic: Start
            self.session_manager.start_session(
                selected_apps,
                self.focus_tab.get_description(),
                focus_tabs=focus_tabs if focus_tabs else None
            )
            
            # 4. UI: Activate
            self.focus_tab.set_active_mode(selected_apps, focus_tabs=focus_tabs if focus_tabs else None)
            self.session_timer.start(1000) 
        else:
            # 1. Logic: Stop
            self.session_timer.stop()
            stats = self.session_manager.stop_session()
            
            # 2. UI: Reset
            self.focus_tab.set_setup_mode()
            
            # 3. Network: Upload
            upload_result = self.network_client.upload_session(stats)

            # 4. Feedback Assembly (Delegated Logic)
            summary = self.session_manager.get_session_summary(stats)
            extra_msg = ""
            
            if upload_result.get("status") == "offline":
                extra_msg = "\n\n⚠️ Currently offline. Session cached locally."
            elif upload_result.get("status") == "success":
                new_ach = upload_result.get("new_achievements", [])
                if new_ach:
                    names = [self.network_client.get_achievement_name(a) for a in new_ach]
                    extra_msg = f"\n\n★ Achievement Unlocked: {', '.join(names)}!"

            QMessageBox.information(self, "Session Complete!", f"{summary}{extra_msg}")

    def update_timer_ui(self):
        """Refreshes the Focus Tab display with current session metrics."""
        total, focus, dists, score = self.session_manager.get_current_stats()
        
        # Format and push data to the View
        time_str = self.session_manager.format_seconds(total)
        self.focus_tab.update_stats(time_str, dists, score)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    # The application style is centralized in style.py
    app.setStyleSheet(GLOBAL_STYLESHEET)
    window = LockInApp()
    window.show()
    sys.exit(app.exec_())