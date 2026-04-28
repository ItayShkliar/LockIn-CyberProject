from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton, QListWidget,
                             QListWidgetItem, QHBoxLayout, QFrame, QLineEdit, QScrollArea)
from PyQt5.QtCore import Qt


class FocusTab(QWidget):
    def __init__(self):
        super().__init__()
        
        # Outer scroll area so everything is accessible on small windows
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        
        inner = QWidget()
        layout = QVBoxLayout(inner)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        
        title = QLabel("Lock In Mode")
        title.setObjectName("Title")
        layout.addWidget(title)
        
        # =====================================================
        # 1. SETUP MODE CARD — App Selection
        # =====================================================
        self.setup_card = QFrame()
        self.setup_card.setObjectName("Card")
        setup_layout = QVBoxLayout(self.setup_card)
        setup_layout.setContentsMargins(20, 20, 20, 20)
        setup_layout.setSpacing(15)
        
        self.desc_input = QLineEdit()
        self.desc_input.setPlaceholderText("What are you focusing on? (e.g., 'Deep Work')")
        setup_layout.addWidget(self.desc_input)
        
        instruct = QLabel("Select the apps you want to track during your session:")
        instruct.setObjectName("Subtitle")
        setup_layout.addWidget(instruct)
        
        self.app_list = QListWidget()
        setup_layout.addWidget(self.app_list)
        
        self.scan_btn = QPushButton("🔄 Refresh Running Apps")
        self.scan_btn.setProperty("theme", "primary")
        setup_layout.addWidget(self.scan_btn)
        
        layout.addWidget(self.setup_card)

        # =====================================================
        # 1b. SETUP MODE CARD — Browser Tab Keywords
        # =====================================================
        self.tabs_card = QFrame()
        self.tabs_card.setObjectName("Card")
        tabs_layout = QVBoxLayout(self.tabs_card)
        tabs_layout.setContentsMargins(20, 20, 20, 20)
        tabs_layout.setSpacing(12)

        tabs_title = QLabel("🌐 Browser Tab Focus (Optional)")
        tabs_title.setObjectName("Subtitle")
        tabs_layout.addWidget(tabs_title)

        tabs_desc = QLabel(
            "If you selected a browser above, enter keywords to specify which "
            "sites count as focused (e.g. 'github', 'docs.google', 'stackoverflow').\n\n"
            "💡 The monitor checks your browser's window title every second.\n"
            "If the title contains any of your keywords → Focused ✅\n"
            "If not → Distraction ❌\n\n"
            "Leave empty to count ALL browser usage as focused."
        )
        tabs_desc.setWordWrap(True)
        tabs_desc.setStyleSheet("color: #94a3b8; font-size: 12px;")
        tabs_layout.addWidget(tabs_desc)

        # Input row: text field + add button
        input_row = QHBoxLayout()
        self.tab_keyword_input = QLineEdit()
        self.tab_keyword_input.setPlaceholderText("Type a keyword (e.g. 'github', 'notion') and press Add...")
        input_row.addWidget(self.tab_keyword_input)

        self.add_tab_btn = QPushButton("+ Add")
        self.add_tab_btn.setProperty("theme", "primary")
        self.add_tab_btn.setFixedWidth(80)
        self.add_tab_btn.clicked.connect(self._add_tab_keyword)
        input_row.addWidget(self.add_tab_btn)
        tabs_layout.addLayout(input_row)

        # List of added keywords
        self.tab_keywords_list = QListWidget()
        self.tab_keywords_list.setMaximumHeight(120)
        tabs_layout.addWidget(self.tab_keywords_list)

        # Scan open browser tabs button
        scan_note = QLabel(
            "⚠️ Scan detects only the currently visible tab per browser window.\n"
            "Switch to each tab you want to track, then scan again."
        )
        scan_note.setWordWrap(True)
        scan_note.setStyleSheet("color: #f59e0b; font-size: 11px;")
        tabs_layout.addWidget(scan_note)

        self.scan_tabs_btn = QPushButton("🔍 Scan Current Browser Tabs")
        self.scan_tabs_btn.setProperty("theme", "primary")
        tabs_layout.addWidget(self.scan_tabs_btn)

        # List of detected browser tabs (checkable)
        self.browser_tabs_list = QListWidget()
        self.browser_tabs_list.setMaximumHeight(150)
        tabs_layout.addWidget(self.browser_tabs_list)

        layout.addWidget(self.tabs_card)

        # =====================================================
        # 2. ACTIVE SESSION CARD
        # =====================================================
        self.active_card = QFrame()
        self.active_card.setObjectName("Card")
        active_layout = QVBoxLayout(self.active_card)
        active_layout.setContentsMargins(20, 20, 20, 20)
        active_layout.setSpacing(20)
        
        self.focus_apps_label = QLabel("🎯 Tracking: None")
        self.focus_apps_label.setObjectName("Subtitle")
        self.focus_apps_label.setAlignment(Qt.AlignCenter)
        self.focus_apps_label.setWordWrap(True)
        active_layout.addWidget(self.focus_apps_label)

        self.focus_tabs_label = QLabel("")
        self.focus_tabs_label.setAlignment(Qt.AlignCenter)
        self.focus_tabs_label.setWordWrap(True)
        self.focus_tabs_label.setStyleSheet("color: #38bdf8; font-size: 13px;")
        active_layout.addWidget(self.focus_tabs_label)
        
        stats_layout = QHBoxLayout()
        self.distractions_label = QLabel("👀 Distractions: 0")
        self.distractions_label.setStyleSheet("font-size: 20px; color: #ef4444; font-weight: bold;")
        
        self.score_label = QLabel("🏆 Focus Score: 100")
        self.score_label.setStyleSheet("font-size: 20px; color: #10b981; font-weight: bold;")
        
        stats_layout.addWidget(self.distractions_label)
        stats_layout.addStretch()
        stats_layout.addWidget(self.score_label)
        active_layout.addLayout(stats_layout)
        
        self.active_card.hide()
        layout.addWidget(self.active_card)

        # =====================================================
        # 3. GLOBAL TIMER & BUTTON
        # =====================================================
        layout.addStretch()
        
        timer_container = QFrame()
        timer_container.setObjectName("Card")
        timer_layout = QVBoxLayout(timer_container)
        
        self.timer_label = QLabel("00:00:00")
        self.timer_label.setStyleSheet("font-size: 80px; font-weight: bold; color: #3b82f6; font-family: 'Consolas', monospace;")
        self.timer_label.setAlignment(Qt.AlignCenter)
        timer_layout.addWidget(self.timer_label)
        layout.addWidget(timer_container)
        
        self.start_btn = QPushButton("LOCK IN")
        self.start_btn.setFixedHeight(60)
        self.start_btn.setProperty("theme", "success")
        self.start_btn.setStyleSheet("font-size: 24px;")
        layout.addWidget(self.start_btn)

        # Wire up the scroll area
        scroll.setWidget(inner)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

    # ==============================================================
    # Tab keyword helpers
    # ==============================================================

    def _add_tab_keyword(self):
        """Adds a keyword from the input field to the keywords list."""
        text = self.tab_keyword_input.text().strip()
        if text:
            item = QListWidgetItem(text)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Checked)
            self.tab_keywords_list.addItem(item)
            self.tab_keyword_input.clear()

    def populate_browser_tabs(self, tabs: list):
        """Populates the browser tabs list with checkable items."""
        self.browser_tabs_list.clear()
        for tab in tabs:
            item = QListWidgetItem(f"🌐 {tab}")
            item.setData(Qt.UserRole, tab)   # store the raw title
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Unchecked)
            self.browser_tabs_list.addItem(item)

    def get_focus_tab_keywords(self) -> list:
        """Returns all active focus tab keywords (typed + checked browser tabs)."""
        keywords = []

        # From manually typed keywords
        for i in range(self.tab_keywords_list.count()):
            item = self.tab_keywords_list.item(i)
            if item.checkState() == Qt.Checked:
                keywords.append(item.text())

        # From checked scanned browser tabs
        for i in range(self.browser_tabs_list.count()):
            item = self.browser_tabs_list.item(i)
            if item.checkState() == Qt.Checked:
                raw = item.data(Qt.UserRole)
                if raw:
                    keywords.append(raw)

        return keywords

    # ==============================================================
    # App list helpers (unchanged)
    # ==============================================================

    def populate_apps(self, apps_list):
        self.app_list.clear()
        for app in apps_list:
            item = QListWidgetItem(app)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Unchecked)
            self.app_list.addItem(item)

    def get_selected_apps(self) -> list:
        selected = []
        for i in range(self.app_list.count()):
            item = self.app_list.item(i)
            if item.checkState() == Qt.Checked:
                selected.append(item.text())
        return selected

    # ==============================================================
    # Mode switching
    # ==============================================================

    def set_active_mode(self, selected_apps: list, focus_tabs: list = None):
        self.setup_card.hide()
        self.tabs_card.hide()
        apps_text = ", ".join(selected_apps)
        self.focus_apps_label.setText(f"🎯 Tracking:\n{apps_text}")

        if focus_tabs:
            self.focus_tabs_label.setText(f"🌐 Focus tabs: {', '.join(focus_tabs)}")
            self.focus_tabs_label.show()
        else:
            self.focus_tabs_label.hide()

        self.distractions_label.setText("👀 Distractions: 0")
        self.score_label.setText("🏆 Focus Score: 100")
        self.active_card.show()
        self.start_btn.setText("STOP SESSION")
        self.start_btn.setProperty("theme", "danger")
        self.start_btn.style().unpolish(self.start_btn)
        self.start_btn.style().polish(self.start_btn)

    def get_description(self) -> str:
        text = self.desc_input.text().strip()
        return text if text else "Focus Session"
    
    def update_stats(self, time_str: str, distractions: int, score: int):
        self.timer_label.setText(time_str)
        self.distractions_label.setText(f"👀 Distractions: {distractions}")
        self.score_label.setText(f"🏆 Focus Score: {score}")
        
        # Dynamic color for score
        score_color = "#10b981" if score >= 70 else "#f59e0b" if score >= 40 else "#ef4444"
        self.score_label.setStyleSheet(f"font-size: 20px; color: {score_color}; font-weight: bold;")

    def set_setup_mode(self):
        self.active_card.hide()
        self.setup_card.show()
        self.tabs_card.show()
        self.timer_label.setText("00:00:00")
        self.focus_tabs_label.hide()
        self.start_btn.setText("LOCK IN")
        self.start_btn.setProperty("theme", "success")
        self.start_btn.style().unpolish(self.start_btn)
        self.start_btn.style().polish(self.start_btn)