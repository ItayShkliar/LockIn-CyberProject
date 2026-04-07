"""
Main Application Entry Point
Orchestrates the UI views and Logic managers.
"""
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QStackedWidget, QMessageBox
from PyQt5.QtCore import QTimer # <-- We need this for the live timer!

# Import UI Views
from ui.login_view import LoginView
from ui.main_window_view import MainWindowView
from ui.tabs.home_tab import HomeTab
from ui.tabs.focus_tab import FocusTab
from ui.tabs.stats_tab import StatsTab
from ui.tabs.settings_tab import SettingsTab

# Import Logic Managers
from logic.network_client import NetworkClient
from logic.session_manager import SessionManager

class LockInApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Lock In - Productivity")
        self.resize(1000, 700) 
        self.setStyleSheet("background-color: #36393F;") 
        
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
        self.home_tab = HomeTab()
        self.focus_tab = FocusTab()
        self.stats_tab = StatsTab()
        self.settings_tab = SettingsTab()
        
        self.main_window.add_tab(self.home_tab)
        self.main_window.add_tab(self.focus_tab)
        self.main_window.add_tab(self.stats_tab)
        self.main_window.add_tab(self.settings_tab)

    def _connect_signals(self):
        self.login_view._login_btn.clicked.connect(self.handle_login)
        
        self.main_window.nav_buttons["home_btn"].clicked.connect(lambda: self.main_window.switch_tab(0))
        self.main_window.nav_buttons["focus_btn"].clicked.connect(lambda: self.main_window.switch_tab(1))
        self.main_window.nav_buttons["stats_btn"].clicked.connect(lambda: self.main_window.switch_tab(2))
        self.main_window.nav_buttons["settings_btn"].clicked.connect(lambda: self.main_window.switch_tab(3))
        self.main_window.logout_btn.clicked.connect(self.handle_logout)
        
        self.focus_tab.scan_btn.clicked.connect(self.scan_and_populate_apps)
        
        # ---> WIRE UP THE START BUTTON <---
        self.focus_tab.start_btn.clicked.connect(self.toggle_session)

    # ==========================================
    # Action Handlers
    # ==========================================
    def handle_login(self):
        self.main_stack.setCurrentWidget(self.main_window)

    def handle_logout(self):
        self.network_client.logged_in_user_id = None
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
            self.focus_tab.scan_btn.setText("🔄 Scan Running Apps")

    def toggle_session(self):
        if not self.session_manager.is_active:
            # 1. Start the Session
            selected_apps = self.focus_tab.get_selected_apps()
            if not selected_apps:
                QMessageBox.warning(self, "Hold Up", "Please scan and select at least one app to focus on!")
                return
                
            self.session_manager.start_session(selected_apps)
            
            # 2. Update UI to "Active" mode (Hides scanner, shows chosen apps)
            self.focus_tab.set_active_mode(selected_apps)
            self.focus_tab.start_btn.setText("STOP SESSION")
            self.focus_tab.start_btn.setStyleSheet("background-color: #E74C3C; color: white; font-size: 24px; font-weight: bold; border-radius: 10px;")
            
            # 3. Start ticking the timer!
            self.session_timer.start(1000) 
        else:
            # 1. Stop the Session
            self.session_timer.stop()
            stats = self.session_manager.stop_session()
            
            # 2. Reset UI back to "Setup" mode (Brings scanner back)
            self.focus_tab.set_setup_mode()
            self.focus_tab.start_btn.setText("LOCK IN")
            self.focus_tab.start_btn.setStyleSheet("background-color: #43B581; color: white; font-size: 24px; font-weight: bold; border-radius: 10px;")
            
            # 3. Show the results!
            QMessageBox.information(self, "Session Complete!", 
                f"Great job!\n\n"
                f"⏱️ Total Time: {stats['total_time_seconds']}s\n"
                f"🎯 Focus Time: {stats['focus_time_seconds']}s\n"
                f"❌ Distractions: {stats['distractions']}\n"
                f"🏆 Final Score: {stats['final_score']}")

    def update_timer_ui(self):
        """Runs every 1 second while a session is active to update the clock and stats."""
        total_sec, focus_sec, dists, score = self.session_manager.get_current_stats()
        
        # Math to format seconds into HH:MM:SS
        m, s = divmod(total_sec, 60)
        h, m = divmod(m, 60)
        time_string = f"{h:02d}:{m:02d}:{s:02d}"
        
        # Update Timer
        self.focus_tab.timer_label.setText(time_string)
        
        # Update Live Stats
        self.focus_tab.distractions_label.setText(f"👀 Distractions: {dists}")
        
        # Optional: Change score color if it drops below 70
        score_color = "#FAA61A" if score >= 70 else "#E74C3C" 
        self.focus_tab.score_label.setStyleSheet(f"font-size: 20px; color: {score_color}; font-weight: bold;")
        self.focus_tab.score_label.setText(f"🏆 Focus Score: {score}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LockInApp()
    window.show()
    sys.exit(app.exec_())