from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QFrame, QHBoxLayout
from PyQt5.QtCore import Qt

class LoginView(QWidget):
    def __init__(self):
        super().__init__()
        self.is_login_mode = True
        self._init_ui()
        
    def _init_ui(self):
        # We want a layout that centers the card
        outer_layout = QVBoxLayout(self)
        outer_layout.setAlignment(Qt.AlignCenter)
        
        # The "Card"
        self.card = QFrame()
        self.card.setObjectName("Card")
        self.card.setFixedWidth(360)
        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(30, 40, 30, 40)
        card_layout.setSpacing(15)
        
        # Title & Subtitle
        title = QLabel("Lock In")
        title.setObjectName("Title")
        title.setAlignment(Qt.AlignCenter)
        
        self._subtitle = QLabel("Welcome back! Please log in.")
        self._subtitle.setObjectName("Subtitle")
        self._subtitle.setAlignment(Qt.AlignCenter)
        self._subtitle.setWordWrap(True)
        
        # Inputs
        self._username_input = QLineEdit()
        self._username_input.setPlaceholderText("Username")
        
        self._email_input = QLineEdit()
        self._email_input.setPlaceholderText("Email")
        self._email_input.hide()
        
        self._password_input = QLineEdit()
        self._password_input.setPlaceholderText("Password")
        self._password_input.setEchoMode(QLineEdit.Password)
        
        # Action Buttons
        self._login_btn = QPushButton("Login")
        self._login_btn.setProperty("theme", "primary")
        self._login_btn.setFixedHeight(45)
        
        self._register_btn = QPushButton("Create Account")
        self._register_btn.setProperty("theme", "success")
        self._register_btn.setFixedHeight(45)
        self._register_btn.hide()
        
        # Mode Switcher Button
        self._switch_mode_btn = QPushButton("Don't have an account? Register")
        self._switch_mode_btn.setCursor(Qt.PointingHandCursor)
        self._switch_mode_btn.setObjectName("NavBtn") # Reusing NavBtn style for link-like look
        self._switch_mode_btn.setStyleSheet("text-align: center; padding-left: 0;") 
        self._switch_mode_btn.clicked.connect(self._toggle_mode)
        
        # Add to card layout
        card_layout.addWidget(title)
        card_layout.addWidget(self._subtitle)
        card_layout.addSpacing(10)
        card_layout.addWidget(self._username_input)
        card_layout.addWidget(self._email_input)
        card_layout.addWidget(self._password_input)
        card_layout.addSpacing(10)
        card_layout.addWidget(self._login_btn)
        card_layout.addWidget(self._register_btn)
        card_layout.addWidget(self._switch_mode_btn)
        
        outer_layout.addWidget(self.card)

    def _toggle_mode(self):
        if self.is_login_mode:
            self._subtitle.setText("Create a new account to join the competition.")
            self._email_input.show()
            self._login_btn.hide()
            self._register_btn.show()
            self._switch_mode_btn.setText("Already have an account? Log in")
            self.is_login_mode = False
        else:
            self._subtitle.setText("Welcome back! Please log in.")
            self._email_input.hide()
            self._login_btn.show()
            self._register_btn.hide()
            self._switch_mode_btn.setText("Don't have an account? Register")
            self.is_login_mode = True