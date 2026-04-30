"""
Centralized QSS Stylesheet for a modern, premium dark-mode UI.
Design inspired by Linear, Notion, and Arc browser aesthetics.
"""

GLOBAL_STYLESHEET = """
/* ================================================================
   FOUNDATION — Base tokens & resets
   ================================================================ */
* {
    outline: none;
}

QWidget {
    background-color: #0a0f1e;
    color: #e2e8f0;
    font-family: 'Segoe UI', 'Inter', 'Roboto', sans-serif;
    font-size: 13px;
}

/* ================================================================
   SIDEBAR
   ================================================================ */
QWidget#Sidebar {
    background-color: #0d1224;
    border-right: 1px solid rgba(59, 130, 246, 0.08);
}

/* Logo container */
QWidget#LogoContainer {
    background: transparent;
}

QLabel#LogoText {
    font-size: 22px;
    font-weight: 800;
    color: #f8fafc;
    letter-spacing: 1px;
}

QLabel#LogoSubtext {
    font-size: 10px;
    color: #475569;
    letter-spacing: 3px;
    font-weight: 600;
}

/* ================================================================
   NAVIGATION BUTTONS
   ================================================================ */
QPushButton#NavBtn {
    text-align: left;
    padding: 10px 16px;
    background-color: transparent;
    color: #64748b;
    border: none;
    border-radius: 10px;
    font-size: 13px;
    font-weight: 600;
    letter-spacing: 0.3px;
}

QPushButton#NavBtn:hover {
    background-color: rgba(59, 130, 246, 0.06);
    color: #94a3b8;
}

QPushButton#NavBtn[active="true"] {
    background-color: rgba(59, 130, 246, 0.12);
    color: #60a5fa;
    border-left: 3px solid #3b82f6;
    padding-left: 13px;
}

/* ================================================================
   CONTENT AREA
   ================================================================ */
QStackedWidget#ContentArea {
    background-color: #0a0f1e;
}

/* ================================================================
   BUTTONS — General
   ================================================================ */
QPushButton {
    background-color: rgba(30, 41, 59, 0.7);
    color: #e2e8f0;
    border: 1px solid rgba(51, 65, 85, 0.5);
    border-radius: 10px;
    padding: 8px 18px;
    font-weight: 600;
    font-size: 13px;
}

QPushButton:hover {
    background-color: rgba(51, 65, 85, 0.6);
    border-color: rgba(71, 85, 105, 0.7);
}

QPushButton:pressed {
    background-color: rgba(15, 23, 42, 0.8);
}

/* Primary */
QPushButton[theme="primary"] {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #2563eb, stop:1 #3b82f6);
    color: white;
    border: none;
}

QPushButton[theme="primary"]:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #1d4ed8, stop:1 #2563eb);
}

/* Success */
QPushButton[theme="success"] {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #059669, stop:1 #10b981);
    color: white;
    border: none;
}

QPushButton[theme="success"]:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #047857, stop:1 #059669);
}

/* Danger */
QPushButton[theme="danger"] {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #dc2626, stop:1 #ef4444);
    color: white;
    border: none;
}

QPushButton[theme="danger"]:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #b91c1c, stop:1 #dc2626);
}

/* Ghost / subtle */
QPushButton[theme="ghost"] {
    background: transparent;
    border: 1px solid rgba(51, 65, 85, 0.4);
    color: #94a3b8;
}

QPushButton[theme="ghost"]:hover {
    background: rgba(30, 41, 59, 0.4);
    color: #e2e8f0;
}

/* ================================================================
   TEXT INPUTS
   ================================================================ */
QLineEdit, QTextEdit, QSpinBox {
    background-color: rgba(15, 23, 42, 0.6);
    border: 1px solid rgba(51, 65, 85, 0.5);
    border-radius: 10px;
    padding: 10px 14px;
    color: #e2e8f0;
    font-size: 13px;
    selection-background-color: rgba(59, 130, 246, 0.3);
}

QLineEdit:focus, QTextEdit:focus, QSpinBox:focus {
    border: 1px solid rgba(59, 130, 246, 0.5);
    background-color: rgba(15, 23, 42, 0.8);
}

QLineEdit::placeholder {
    color: #475569;
}

/* ================================================================
   LISTS & TABLES
   ================================================================ */
QListWidget {
    background-color: rgba(13, 18, 36, 0.6);
    border: 1px solid rgba(51, 65, 85, 0.3);
    border-radius: 10px;
    padding: 4px;
    outline: none;
}

QListWidget::item {
    padding: 8px 12px;
    border-radius: 6px;
    margin: 2px 4px;
    color: #94a3b8;
}

QListWidget::item:hover {
    background-color: rgba(59, 130, 246, 0.06);
}

QListWidget::item:selected {
    background-color: rgba(59, 130, 246, 0.12);
    color: #60a5fa;
}

QTableWidget {
    background-color: rgba(13, 18, 36, 0.6);
    border: 1px solid rgba(51, 65, 85, 0.3);
    border-radius: 10px;
    gridline-color: rgba(51, 65, 85, 0.2);
    outline: none;
    selection-background-color: rgba(59, 130, 246, 0.1);
    alternate-background-color: rgba(15, 23, 42, 0.4);
}

QTableWidget::item {
    padding: 8px 12px;
    color: #cbd5e1;
    border-bottom: 1px solid rgba(51, 65, 85, 0.15);
}

QTableWidget::item:selected {
    background-color: rgba(59, 130, 246, 0.12);
    color: #60a5fa;
}

QHeaderView::section {
    background-color: rgba(13, 18, 36, 0.8);
    color: #475569;
    padding: 10px 12px;
    border: none;
    border-bottom: 1px solid rgba(51, 65, 85, 0.3);
    font-weight: 700;
    text-transform: uppercase;
    font-size: 10px;
    letter-spacing: 1px;
}

/* ================================================================
   TAB WIDGET (sub-tabs inside pages)
   ================================================================ */
QTabWidget::pane {
    border: 1px solid rgba(51, 65, 85, 0.2);
    background-color: rgba(13, 18, 36, 0.4);
    border-radius: 12px;
    top: -1px;
}

QTabBar::tab {
    background-color: transparent;
    color: #475569;
    padding: 10px 22px;
    border-top-left-radius: 10px;
    border-top-right-radius: 10px;
    margin-right: 2px;
    font-weight: 700;
    font-size: 12px;
    letter-spacing: 0.5px;
    min-height: 20px;
    min-width: 100px;
}

QTabBar {
    qproperty-elideMode: 0;
}

QTabBar::tab:hover {
    color: #94a3b8;
    background-color: rgba(30, 41, 59, 0.3);
}

QTabBar::tab:selected {
    color: #60a5fa;
    background-color: rgba(59, 130, 246, 0.08);
    border-bottom: 2px solid #3b82f6;
    padding-bottom: 8px;
}

/* ================================================================
   SCROLLBARS — Ultra minimal
   ================================================================ */
QScrollBar:vertical {
    border: none;
    background: transparent;
    width: 6px;
    margin: 0;
}

QScrollBar::handle:vertical {
    background: rgba(51, 65, 85, 0.4);
    min-height: 30px;
    border-radius: 3px;
}

QScrollBar::handle:vertical:hover {
    background: rgba(71, 85, 105, 0.6);
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}

QScrollBar:horizontal {
    border: none;
    background: transparent;
    height: 6px;
    margin: 0;
}

QScrollBar::handle:horizontal {
    background: rgba(51, 65, 85, 0.4);
    min-width: 30px;
    border-radius: 3px;
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0;
}

QScrollArea {
    border: none;
    background: transparent;
}

/* ================================================================
   LABELS — Semantic
   ================================================================ */
QLabel#Title {
    font-size: 28px;
    font-weight: 800;
    color: #f8fafc;
    letter-spacing: -0.5px;
}

QLabel#Subtitle {
    font-size: 13px;
    color: #64748b;
    font-weight: 500;
}

QLabel#SectionHeader {
    font-size: 11px;
    font-weight: 700;
    color: #475569;
    letter-spacing: 1.5px;
}

/* ================================================================
   CARDS / FRAMES
   ================================================================ */
QFrame#Card {
    background-color: rgba(13, 18, 36, 0.7);
    border-radius: 14px;
    border: 1px solid rgba(51, 65, 85, 0.2);
}

QFrame#Card:hover {
    border-color: rgba(59, 130, 246, 0.15);
}

QFrame#GlowCard {
    background-color: rgba(13, 18, 36, 0.7);
    border-radius: 14px;
    border: 1px solid rgba(59, 130, 246, 0.15);
}

/* ================================================================
   COMBOBOX
   ================================================================ */
QComboBox {
    background-color: rgba(15, 23, 42, 0.6);
    border: 1px solid rgba(51, 65, 85, 0.5);
    border-radius: 8px;
    padding: 6px 12px;
    color: #e2e8f0;
    font-size: 12px;
}

QComboBox::drop-down {
    border: none;
    width: 20px;
}

QComboBox QAbstractItemView {
    background-color: #0d1224;
    border: 1px solid rgba(51, 65, 85, 0.3);
    selection-background-color: rgba(59, 130, 246, 0.15);
    color: #e2e8f0;
}

/* ================================================================
   CHECKBOX
   ================================================================ */
QCheckBox {
    color: #94a3b8;
    font-size: 13px;
    spacing: 8px;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 4px;
    border: 1px solid rgba(51, 65, 85, 0.5);
    background-color: rgba(15, 23, 42, 0.6);
}

QCheckBox::indicator:checked {
    background-color: #3b82f6;
    border-color: #3b82f6;
}

/* ================================================================
   DATE/TIME EDIT
   ================================================================ */
QDateTimeEdit {
    background-color: rgba(15, 23, 42, 0.6);
    border: 1px solid rgba(51, 65, 85, 0.5);
    border-radius: 8px;
    padding: 8px 12px;
    color: #e2e8f0;
}

/* ================================================================
   TOOLTIP
   ================================================================ */
QToolTip {
    background-color: #1e293b;
    color: #e2e8f0;
    border: 1px solid rgba(51, 65, 85, 0.3);
    border-radius: 6px;
    padding: 6px 10px;
    font-size: 12px;
}

/* ================================================================
   MESSAGE BOX
   ================================================================ */
QMessageBox {
    background-color: #0d1224;
}

QMessageBox QLabel {
    color: #e2e8f0;
    font-size: 13px;
}
"""
