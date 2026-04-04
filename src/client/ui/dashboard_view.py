"""
Dashboard View Module
The main screen showing user statistics, focus score, and session controls.
"""
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame
from PyQt5.QtCore import Qt

class DashboardView(QWidget):
    """
    מחלקה המייצגת את המסך הראשי של המערכת (Dashboard).
    מציגה נתונים סטטיסטיים וכפתור להתחלת סשן ריכוז.
    """
    def __init__(self):
        super().__init__()
        self._init_ui()
        
    def _init_ui(self):
        # פריסה ראשית
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)
        
        # כותרת שלום למשתמש
        self._welcome_label = QLabel("ברוך שובך, משתמש!")
        self._welcome_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #2C3E50;")
        self._welcome_label.setAlignment(Qt.AlignCenter)
        
        # קופסת נתונים (סטטיסטיקות לפי מסמך העיצוב)
        stats_layout = QHBoxLayout()
        
        # יצירת קוביות המידע (Score, Time, Distractions)
        self._score_label = self._create_stat_box("Focus Score", "100")
        self._time_label = self._create_stat_box("זמן פוקוס", "00:00:00")
        self._distractions_label = self._create_stat_box("הסחות דעת", "0")
        
        stats_layout.addWidget(self._score_label)
        stats_layout.addWidget(self._time_label)
        stats_layout.addWidget(self._distractions_label)
        
        # כפתור התחלת סשן (Lock In)
        self._start_session_btn = QPushButton("Lock In! (התחל סשן)")
        self._start_session_btn.setFixedSize(250, 60)
        self._start_session_btn.setStyleSheet("""
            QPushButton {
                background-color: #E74C3C; 
                color: white; 
                font-size: 20px; 
                font-weight: bold;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #C0392B;
            }
        """)
        
        # סידור הכפתור באמצע
        btn_layout = QHBoxLayout()
        btn_layout.setAlignment(Qt.AlignCenter)
        btn_layout.addWidget(self._start_session_btn)
        
        # חיבור הרכיבים לפריסה הראשית
        main_layout.addWidget(self._welcome_label)
        main_layout.addLayout(stats_layout)
        main_layout.addStretch() # דוחף את הכפתור קצת למטה
        main_layout.addLayout(btn_layout)
        
        self.setLayout(main_layout)
        
    def _create_stat_box(self, title: str, value: str) -> QFrame:
        """פונקציית עזר ליצירת קוביות נתונים יפות למסך הראשי"""
        frame = QFrame()
        frame.setStyleSheet("background-color: #ECF0F1; border-radius: 10px; padding: 15px;")
        layout = QVBoxLayout()
        
        title_lbl = QLabel(title)
        title_lbl.setStyleSheet("font-size: 14px; color: #7F8C8D;")
        title_lbl.setAlignment(Qt.AlignCenter)
        
        value_lbl = QLabel(value)
        value_lbl.setStyleSheet("font-size: 28px; font-weight: bold; color: #2C3E50;")
        value_lbl.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(title_lbl)
        layout.addWidget(value_lbl)
        frame.setLayout(layout)
        return frame