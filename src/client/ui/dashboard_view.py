"""
Dashboard View Module
The main screen showing user statistics, focus score, and session controls.
"""
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame
from PyQt5.QtCore import Qt

class DashboardView(QWidget):
    def __init__(self):
        super().__init__()
        self._init_ui()
        
    def _init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)
        
        top_layout = QHBoxLayout()
        self._settings_btn = QPushButton("⚙️ Settings (Choose Apps)")
        self._settings_btn.setStyleSheet("padding: 8px; background-color: #7F8C8D; color: white; font-weight: bold; border-radius: 5px;")
        self._settings_btn.setFixedSize(180, 40)
        top_layout.addStretch() 
        top_layout.addWidget(self._settings_btn)
        
        self._welcome_label = QLabel("Welcome back, User!")
        self._welcome_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #2C3E50;")
        self._welcome_label.setAlignment(Qt.AlignCenter)
        
        stats_layout = QHBoxLayout()
        # Create the boxes and save the reference to the actual text labels!
        score_frame, self.lbl_score_val = self._create_stat_box("Focus Score", "100")
        time_frame, self.lbl_time_val = self._create_stat_box("Focus Time", "00:00:00")
        dist_frame, self.lbl_dist_val = self._create_stat_box("Distractions", "0")
        
        stats_layout.addWidget(score_frame)
        stats_layout.addWidget(time_frame)
        stats_layout.addWidget(dist_frame)
        
        self._start_session_btn = QPushButton("Lock In! (Start Session)")
        self._start_session_btn.setFixedSize(250, 60)
        self._start_session_btn.setStyleSheet("""
            QPushButton { background-color: #E74C3C; color: white; font-size: 20px; font-weight: bold; border-radius: 10px; }
            QPushButton:hover { background-color: #C0392B; }
        """)
        
        btn_layout = QHBoxLayout()
        btn_layout.setAlignment(Qt.AlignCenter)
        btn_layout.addWidget(self._start_session_btn)
        
        main_layout.addLayout(top_layout)
        main_layout.addWidget(self._welcome_label)
        main_layout.addLayout(stats_layout)
        main_layout.addStretch() 
        main_layout.addLayout(btn_layout)
        self.setLayout(main_layout)
        
    def _create_stat_box(self, title: str, value: str):
        """Helper to create stat boxes. Returns the frame AND the value label."""
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
        
        return frame, value_lbl

    def update_stats(self, time_str: str, score: str, distractions: str):
        """Called every second by main.py to update the live UI."""
        self.lbl_time_val.setText(time_str)
        self.lbl_score_val.setText(score)
        self.lbl_dist_val.setText(distractions)