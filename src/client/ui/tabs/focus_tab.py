"""
Focus Tab — Session setup, active monitoring, and timer.
Clean two-state UI: setup mode ↔ active session mode.
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton, QListWidget,
                             QListWidgetItem, QHBoxLayout, QFrame, QLineEdit,
                             QScrollArea, QGraphicsDropShadowEffect)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor


class FocusTab(QWidget):
    def __init__(self):
        super().__init__()

        # Outer scroll area so everything is accessible on small windows
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        inner = QWidget()
        layout = QVBoxLayout(inner)
        layout.setContentsMargins(44, 44, 44, 44)
        layout.setSpacing(24)

        title = QLabel("Focus Mode")
        title.setObjectName("Title")
        layout.addWidget(title)

        subtitle = QLabel("Select your apps, set your intent, and lock in.")
        subtitle.setStyleSheet("color: #475569; font-size: 13px; margin-bottom: 4px;")
        layout.addWidget(subtitle)

        # =====================================================
        # 1. SETUP MODE CARD — App Selection
        # =====================================================
        self.setup_card = QFrame()
        self.setup_card.setObjectName("Card")
        setup_layout = QVBoxLayout(self.setup_card)
        setup_layout.setContentsMargins(24, 24, 24, 24)
        setup_layout.setSpacing(14)

        # Description input
        desc_label = QLabel("WHAT ARE YOU WORKING ON?")
        desc_label.setObjectName("SectionHeader")
        setup_layout.addWidget(desc_label)

        self.desc_input = QLineEdit()
        self.desc_input.setPlaceholderText("e.g. Deep Work, Studying, Coding...")
        self.desc_input.setFixedHeight(42)
        setup_layout.addWidget(self.desc_input)

        setup_layout.addSpacing(6)

        apps_label = QLabel("SELECT APPS TO TRACK")
        apps_label.setObjectName("SectionHeader")
        setup_layout.addWidget(apps_label)

        self.app_list = QListWidget()
        self.app_list.setMinimumHeight(140)
        setup_layout.addWidget(self.app_list)

        self.scan_btn = QPushButton("↻  Refresh Running Apps")
        self.scan_btn.setProperty("theme", "primary")
        self.scan_btn.setFixedHeight(38)
        self.scan_btn.setCursor(Qt.PointingHandCursor)
        setup_layout.addWidget(self.scan_btn)

        layout.addWidget(self.setup_card)

        # =====================================================
        # 1b. SETUP MODE CARD — Browser Tab Keywords
        # =====================================================
        self.tabs_card = QFrame()
        self.tabs_card.setObjectName("Card")
        tabs_layout = QVBoxLayout(self.tabs_card)
        tabs_layout.setContentsMargins(24, 24, 24, 24)
        tabs_layout.setSpacing(12)

        tabs_title = QLabel("BROWSER TAB FOCUS")
        tabs_title.setObjectName("SectionHeader")
        tabs_layout.addWidget(tabs_title)

        tabs_subtitle = QLabel("Optional")
        tabs_subtitle.setStyleSheet(
            "font-size: 11px; color: #334155; font-weight: 500; margin-bottom: 4px;"
        )
        tabs_layout.addWidget(tabs_subtitle)

        tabs_desc = QLabel(
            "If you selected a browser above, enter keywords to specify which "
            "sites count as focused (e.g. 'github', 'docs.google').\n\n"
            "The monitor checks your browser's title every second.\n"
            "Match → Focused ✓   No match → Distraction ✗\n\n"
            "Leave empty to count all browser usage as focused."
        )
        tabs_desc.setWordWrap(True)
        tabs_desc.setStyleSheet("color: #334155; font-size: 12px; line-height: 1.5;")
        tabs_layout.addWidget(tabs_desc)

        # Input row: text field + add button
        input_row = QHBoxLayout()
        self.tab_keyword_input = QLineEdit()
        self.tab_keyword_input.setPlaceholderText("Type a keyword and press Add...")
        self.tab_keyword_input.setFixedHeight(38)
        input_row.addWidget(self.tab_keyword_input)

        self.add_tab_btn = QPushButton("+ Add")
        self.add_tab_btn.setProperty("theme", "primary")
        self.add_tab_btn.setFixedWidth(80)
        self.add_tab_btn.setFixedHeight(38)
        self.add_tab_btn.setCursor(Qt.PointingHandCursor)
        self.add_tab_btn.clicked.connect(self._add_tab_keyword)
        input_row.addWidget(self.add_tab_btn)
        tabs_layout.addLayout(input_row)

        # List of added keywords
        self.tab_keywords_list = QListWidget()
        self.tab_keywords_list.setMaximumHeight(100)
        tabs_layout.addWidget(self.tab_keywords_list)

        # Scan open browser tabs button
        scan_note = QLabel(
            "⚠ Scan detects only the currently visible tab per browser window."
        )
        scan_note.setWordWrap(True)
        scan_note.setStyleSheet("color: #92400e; font-size: 11px; margin-top: 4px;")
        tabs_layout.addWidget(scan_note)

        self.scan_tabs_btn = QPushButton("🔍  Scan Current Browser Tabs")
        self.scan_tabs_btn.setProperty("theme", "primary")
        self.scan_tabs_btn.setFixedHeight(38)
        self.scan_tabs_btn.setCursor(Qt.PointingHandCursor)
        tabs_layout.addWidget(self.scan_tabs_btn)

        # List of detected browser tabs (checkable)
        self.browser_tabs_list = QListWidget()
        self.browser_tabs_list.setMaximumHeight(120)
        tabs_layout.addWidget(self.browser_tabs_list)

        layout.addWidget(self.tabs_card)

        # =====================================================
        # 2. ACTIVE SESSION CARD
        # =====================================================
        self.active_card = QFrame()
        self.active_card.setObjectName("GlowCard")
        active_layout = QVBoxLayout(self.active_card)
        active_layout.setContentsMargins(28, 24, 28, 24)
        active_layout.setSpacing(16)

        self.focus_apps_label = QLabel("🎯 Tracking: None")
        self.focus_apps_label.setStyleSheet(
            "font-size: 14px; font-weight: 600; color: #94a3b8; background: transparent;"
        )
        self.focus_apps_label.setAlignment(Qt.AlignCenter)
        self.focus_apps_label.setWordWrap(True)
        active_layout.addWidget(self.focus_apps_label)

        self.focus_tabs_label = QLabel("")
        self.focus_tabs_label.setAlignment(Qt.AlignCenter)
        self.focus_tabs_label.setWordWrap(True)
        self.focus_tabs_label.setStyleSheet(
            "color: #38bdf8; font-size: 12px; background: transparent;"
        )
        active_layout.addWidget(self.focus_tabs_label)

        stats_layout = QHBoxLayout()
        self.distractions_label = QLabel("Distractions: 0")
        self.distractions_label.setStyleSheet(
            "font-size: 18px; color: #f87171; font-weight: 700; background: transparent;"
        )

        self.score_label = QLabel("Score: 100")
        self.score_label.setStyleSheet(
            "font-size: 18px; color: #34d399; font-weight: 700; background: transparent;"
        )

        stats_layout.addWidget(self.distractions_label)
        stats_layout.addStretch()
        stats_layout.addWidget(self.score_label)
        active_layout.addLayout(stats_layout)

        # Glow effect for active card
        glow = QGraphicsDropShadowEffect()
        glow.setBlurRadius(40)
        glow.setColor(QColor(59, 130, 246, 25))
        glow.setOffset(0, 0)
        self.active_card.setGraphicsEffect(glow)

        self.active_card.hide()
        layout.addWidget(self.active_card)

        # =====================================================
        # 3. GLOBAL TIMER & BUTTON
        # =====================================================
        layout.addStretch()

        timer_container = QFrame()
        timer_container.setObjectName("Card")
        timer_container.setStyleSheet("""
            QFrame#Card {
                background-color: rgba(13, 18, 36, 0.5);
                border: 1px solid rgba(51, 65, 85, 0.15);
            }
        """)
        timer_layout = QVBoxLayout(timer_container)
        timer_layout.setContentsMargins(20, 16, 20, 16)

        self.timer_label = QLabel("00:00:00")
        self.timer_label.setStyleSheet(
            "font-size: 72px; font-weight: 800; color: #60a5fa; "
            "font-family: 'Consolas', 'SF Mono', monospace; "
            "letter-spacing: 2px; background: transparent;"
        )
        self.timer_label.setAlignment(Qt.AlignCenter)
        timer_layout.addWidget(self.timer_label)
        layout.addWidget(timer_container)

        self.start_btn = QPushButton("LOCK IN")
        self.start_btn.setFixedHeight(56)
        self.start_btn.setProperty("theme", "success")
        self.start_btn.setCursor(Qt.PointingHandCursor)
        self.start_btn.setStyleSheet("""
            QPushButton {
                font-size: 18px;
                font-weight: 800;
                letter-spacing: 2px;
                border-radius: 14px;
            }
        """)
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

        self.distractions_label.setText("Distractions: 0")
        self.score_label.setText("Score: 100")
        self.active_card.show()
        self.start_btn.setText("STOP SESSION")
        self.start_btn.setProperty("theme", "danger")
        self.start_btn.setStyleSheet("""
            QPushButton {
                font-size: 18px;
                font-weight: 800;
                letter-spacing: 2px;
                border-radius: 14px;
            }
        """)
        self.start_btn.style().unpolish(self.start_btn)
        self.start_btn.style().polish(self.start_btn)

    def get_description(self) -> str:
        text = self.desc_input.text().strip()
        return text if text else "Focus Session"

    def update_stats(self, time_str: str, distractions: int, score: int):
        self.timer_label.setText(time_str)
        self.distractions_label.setText(f"Distractions: {distractions}")
        self.score_label.setText(f"Score: {score}")

        # Dynamic color for score
        if score >= 70:
            score_color = "#34d399"
        elif score >= 40:
            score_color = "#fbbf24"
        else:
            score_color = "#f87171"
        self.score_label.setStyleSheet(
            f"font-size: 18px; color: {score_color}; font-weight: 700; background: transparent;"
        )

    def set_setup_mode(self):
        self.active_card.hide()
        self.setup_card.show()
        self.tabs_card.show()
        self.timer_label.setText("00:00:00")
        self.focus_tabs_label.hide()
        self.start_btn.setText("LOCK IN")
        self.start_btn.setProperty("theme", "success")
        self.start_btn.setStyleSheet("""
            QPushButton {
                font-size: 18px;
                font-weight: 800;
                letter-spacing: 2px;
                border-radius: 14px;
            }
        """)
        self.start_btn.style().unpolish(self.start_btn)
        self.start_btn.style().polish(self.start_btn)