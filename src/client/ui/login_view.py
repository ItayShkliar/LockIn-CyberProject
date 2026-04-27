"""
Login View Module
The first screen the user sees to authenticate or create an account.
"""
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton
from PyQt5.QtCore import Qt

class LoginView(QWidget):
    def __init__(self):
        super().__init__()
        self.is_login_mode = True  # We start in Login Mode by default
        self._init_ui()
        
    def _init_ui(self):
        self.setStyleSheet("background-color: #F4F7FB;")

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(16)
        
        # Title & Subtitle
        title = QLabel("Lock In")
        title.setStyleSheet("font-size: 36px; font-weight: bold; color: #162A44;")
        title.setAlignment(Qt.AlignCenter)
        
        self._subtitle = QLabel("Welcome back! Please log in.")
        self._subtitle.setStyleSheet("font-size: 16px; color: #3F5368; margin-bottom: 20px;")
        self._subtitle.setAlignment(Qt.AlignCenter)
        
        # Inputs
        input_style = (
            "background-color: white;"
            "border: 1px solid #CBD2E0;"
            "border-radius: 8px;"
            "padding: 10px;"
            "color: #162A44;"
            "font-size: 14px;"
        )

        self._username_input = QLineEdit()
        self._username_input.setPlaceholderText("Username")
        self._username_input.setFixedSize(280, 44)
        self._username_input.setStyleSheet(input_style)
        
        self._email_input = QLineEdit()
        self._email_input.setPlaceholderText("Email")
        self._email_input.setFixedSize(280, 44)
        self._email_input.setStyleSheet(input_style)
        self._email_input.hide() # HIDDEN BY DEFAULT!
        
        self._password_input = QLineEdit()
        self._password_input.setPlaceholderText("Password")
        self._password_input.setEchoMode(QLineEdit.Password)
        self._password_input.setFixedSize(280, 44)
        self._password_input.setStyleSheet(input_style)
        
        # Action Buttons
        self._login_btn = QPushButton("Login")
        self._login_btn.setFixedSize(280, 44)
        self._login_btn.setStyleSheet(
            "background-color: #2F80ED;"
            "color: white;"
            "font-weight: bold;"
            "border-radius: 8px;"
            "border: none;"
        )
        
        self._register_btn = QPushButton("Create Account")
        self._register_btn.setFixedSize(280, 44)
        self._register_btn.setStyleSheet(
            "background-color: #16A34A;"
            "color: white;"
            "font-weight: bold;"
            "border-radius: 8px;"
            "border: none;"
        )
        self._register_btn.hide() # HIDDEN BY DEFAULT!
        
        # Mode Switcher Button (Looks like a text link)
        self._switch_mode_btn = QPushButton("Don't have an account? Register here.")
        self._switch_mode_btn.setCursor(Qt.PointingHandCursor)
        self._switch_mode_btn.setStyleSheet(
            "color: #2F80ED;"
            "background: transparent;"
            "border: none;"
            "font-size: 14px;"
            "text-decoration: underline;"
        )
        self._switch_mode_btn.clicked.connect(self._toggle_mode)
        
        # Add everything to the layout
        layout.addWidget(title)
        layout.addWidget(self._subtitle)
        layout.addWidget(self._username_input, alignment=Qt.AlignCenter)
        layout.addWidget(self._email_input, alignment=Qt.AlignCenter)
        layout.addWidget(self._password_input, alignment=Qt.AlignCenter)
        
        # Add some spacing before buttons
        layout.addSpacing(12)
        layout.addWidget(self._login_btn, alignment=Qt.AlignCenter)
        layout.addWidget(self._register_btn, alignment=Qt.AlignCenter)
        layout.addSpacing(12)
        layout.addWidget(self._switch_mode_btn, alignment=Qt.AlignCenter)
        
        self.setLayout(layout)

    def _toggle_mode(self):
        """Switches the UI between Login and Register modes."""
        if self.is_login_mode:
            # Switch TO Register Mode
            self._subtitle.setText("Create a new account to join the competition.")
            self._email_input.show()
            self._login_btn.hide()
            self._register_btn.show()
            self._switch_mode_btn.setText("Already have an account? Log in.")
            self.is_login_mode = False
        else:
            # Switch TO Login Mode
            self._subtitle.setText("Welcome back! Please log in.")
            self._email_input.hide()
            self._login_btn.show()
            self._register_btn.hide()
            self._switch_mode_btn.setText("Don't have an account? Register here.")
            self.is_login_mode = True