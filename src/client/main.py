"""
Client Application Entry Point
Manages the main window and navigation between different views.
"""
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QStackedWidget
from ui.login_view import LoginView
from ui.dashboard_view import DashboardView

class LockInApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Lock In - Focus App")
        self.setFixedSize(800, 600)
        
        # ה-QStackedWidget מאפשר לנו להחזיק כמה מסכים ולהחליף ביניהם
        self._stacked_widget = QStackedWidget()
        self.setCentralWidget(self._stacked_widget)
        
        # יצירת המסכים
        self._login_view = LoginView()
        self._dashboard_view = DashboardView()
        
        # הוספת המסכים לערימה
        self._stacked_widget.addWidget(self._login_view)
        self._stacked_widget.addWidget(self._dashboard_view)
        
        # קשירת כפתור ההתחברות לפונקציה שמחליפה מסך (לבינתיים מעבר ישיר)
        # בפועל, כאן נבדוק קודם סיסמה ורק אם נכונה נעבור מסך
        self._login_view._login_btn.clicked.connect(self._go_to_dashboard)
        
    def _go_to_dashboard(self):
        """פונקציה המעבירה את המשתמש למסך הראשי"""
        # מקבל את שם המשתמש מהמסך הקודם
        username = self._login_view._username_input.text()
        if username:
            self._dashboard_view._welcome_label.setText(f"ברוך שובך, {username}!")
            
        # מעביר את התצוגה למסך מס' 1 בערימה (ה-Dashboard)
        self._stacked_widget.setCurrentIndex(1)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LockInApp()
    window.show()
    sys.exit(app.exec_())