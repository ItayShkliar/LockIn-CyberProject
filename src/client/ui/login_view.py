"""
Login View Module for Lock In
Handles the user interface for the login and registration screen.
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QMessageBox, QHBoxLayout)
from PyQt5.QtCore import Qt

class LoginView(QWidget):
    """
    מחלקה המייצגת את מסך ההתחברות של המערכת.
    כוללת שדות להזנת שם משתמש וסיסמה, וכפתורי התחברות והרשמה.
    """
    
    def __init__(self):
        super().__init__()
        self._init_ui()
        
    def _init_ui(self):
        """
        פונקציה פרטית לאתחול ובניית רכיבי הממשק (Widgets) וסידורם על המסך.
        """
        # הגדרות חלון בסיסיות (למרות שיוצג בתוך חלון ראשי בהמשך)
        self.setWindowTitle("Lock In - Login")
        self.setFixedSize(400, 500)
        
        # פריסה (Layout) ראשית אנכית
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignCenter)
        main_layout.setSpacing(20)
        
        # כותרת האפליקציה
        title_label = QLabel("Lock In")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 36px; font-weight: bold; color: #2C3E50;")
        
        # שדה שם משתמש
        self._username_input = QLineEdit()
        self._username_input.setPlaceholderText("שם משתמש")
        self._username_input.setStyleSheet("font-size: 16px; padding: 10px;")
        
        # שדה סיסמה (מוסתרת)
        self._password_input = QLineEdit()
        self._password_input.setPlaceholderText("סיסמה")
        self._password_input.setEchoMode(QLineEdit.Password)
        self._password_input.setStyleSheet("font-size: 16px; padding: 10px;")
        
        # פריסה אופקית לכפתורים
        buttons_layout = QHBoxLayout()
        
        # כפתור התחברות
        self._login_btn = QPushButton("התחבר")
        self._login_btn.setStyleSheet("font-size: 16px; padding: 10px; background-color: #3498DB; color: white; font-weight: bold;")
        self._login_btn.clicked.connect(self._handle_login)
        
        # כפתור הרשמה
        self._register_btn = QPushButton("הרשם")
        self._register_btn.setStyleSheet("font-size: 16px; padding: 10px; background-color: #2ECC71; color: white; font-weight: bold;")
        self._register_btn.clicked.connect(self._handle_register)
        
        buttons_layout.addWidget(self._login_btn)
        buttons_layout.addWidget(self._register_btn)
        
        # הוספת כל הרכיבים לפריסה הראשית
        main_layout.addWidget(title_label)
        main_layout.addWidget(self._username_input)
        main_layout.addWidget(self._password_input)
        main_layout.addLayout(buttons_layout)
        
        self.setLayout(main_layout)

    def _handle_login(self):
        """
        פונקציה המופעלת בעת לחיצה על כפתור התחברות.
        בהמשך נחבר אותה ללוגיקת האבטחה והרשת.
        """
        username = self._username_input.text()
        password = self._password_input.text()
        
        if not username or not password:
            QMessageBox.warning(self, "שגיאה", "אנא הזן שם משתמש וסיסמה.")
            return
            
        print(f"Attempting to login with Username: {username}")
        # כאן תהיה קריאה למחלקת הלוגיקה שתבדוק את הסיסמה מול השרת

    def _handle_register(self):
        """
        פונקציה המופעלת בעת לחיצה על כפתור הרשמה.
        """
        print("Navigate to Registration screen...")
        QMessageBox.information(self, "הרשמה", "מעבר למסך הרשמה (יפותח בהמשך)")

# קוד קטן לבדיקה מהירה של המסך
if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = LoginView()
    window.show()
    sys.exit(app.exec_())