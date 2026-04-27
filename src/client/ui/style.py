"""
Centralized QSS Stylesheet for a modern, premium look.
"""

GLOBAL_STYLESHEET = """
/* General Background and Defaults */
QWidget {
    background-color: #0f172a;
    color: #f8fafc;
    font-family: 'Segoe UI', 'Roboto', sans-serif;
    font-size: 14px;
}

/* Sidebar Specific */
QWidget#Sidebar {
    background-color: #1e293b;
    border-right: 1px solid #334155;
}

QWidget#Sidebar QLabel#Logo {
    font-size: 24px;
    font-weight: bold;
    color: #3b82f6;
    margin-bottom: 20px;
    padding: 10px;
}

/* Content Area */
QStackedWidget#ContentArea {
    background-color: #0f172a;
}

/* PushButtons */
QPushButton {
    background-color: #334155;
    color: #f8fafc;
    border: none;
    border-radius: 8px;
    padding: 8px 16px;
    font-weight: 600;
}

QPushButton:hover {
    background-color: #475569;
}

QPushButton:pressed {
    background-color: #1e293b;
}

/* Primary Action Buttons */
QPushButton[theme="primary"] {
    background-color: #3b82f6;
}

QPushButton[theme="primary"]:hover {
    background-color: #2563eb;
}

/* Success Buttons */
QPushButton[theme="success"] {
    background-color: #10b981;
}

QPushButton[theme="success"]:hover {
    background-color: #059669;
}

/* Danger Buttons */
QPushButton[theme="danger"] {
    background-color: #ef4444;
}

QPushButton[theme="danger"]:hover {
    background-color: #dc2626;
}

/* Sidebar Buttons */
QPushButton#NavBtn {
    text-align: left;
    padding-left: 20px;
    background-color: transparent;
    color: #94a3b8;
    border-radius: 6px;
    font-size: 15px;
}

QPushButton#NavBtn:hover {
    background-color: #334155;
    color: #f8fafc;
}

QPushButton#NavBtn[active="true"] {
    background-color: #3b82f6;
    color: white;
}

/* Inputs */
QLineEdit {
    background-color: #1e293b;
    border: 1px solid #334155;
    border-radius: 8px;
    padding: 10px;
    color: #f8fafc;
    selection-background-color: #3b82f6;
}

QLineEdit:focus {
    border: 2px solid #3b82f6;
}

/* Lists and Tables */
QListWidget, QTableWidget {
    background-color: #1e293b;
    border: 1px solid #334155;
    border-radius: 8px;
    gridline-color: transparent;
    outline: none;
}

QTableWidget {
    selection-background-color: #334155;
    alternate-background-color: #1a2333;
}

QListWidget::item, QTableWidget::item {
    padding: 12px;
    border-bottom: 1px solid #334155;
    color: #cbd5e1;
}

QListWidget::item:selected, QTableWidget::item:selected {
    background-color: #334155;
    color: #3b82f6;
    border-left: 3px solid #3b82f6;
}

QHeaderView::section {
    background-color: #1e293b;
    color: #94a3b8;
    padding: 10px;
    border: none;
    border-bottom: 2px solid #334155;
    font-weight: bold;
    text-transform: uppercase;
    font-size: 11px;
}

/* Tab Widget Customization */
QTabWidget::pane {
    border: 1px solid #334155;
    background-color: #1e293b;
    border-radius: 8px;
    top: -1px;
}

QTabBar::tab {
    background-color: #0f172a;
    color: #94a3b8;
    padding: 10px 20px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    margin-right: 2px;
    font-weight: bold;
    font-size: 13px;
    min-height: 20px; /* Force internal height */
}

QTabBar::tab:hover {
    background-color: #1e293b;
    color: #f8fafc;
}

QTabBar::tab:selected {
    background-color: #1e293b;
    color: #3b82f6;
    border-bottom: 3px solid #3b82f6;
    padding-bottom: 7px; /* Compensate for border */
}

/* ScrollBars */
QScrollBar:vertical {
    border: none;
    background: #0f172a;
    width: 10px;
    margin: 0px 0px 0px 0px;
}

QScrollBar::handle:vertical {
    background: #334155;
    min-height: 20px;
    border-radius: 5px;
}

QScrollBar::handle:vertical:hover {
    background: #475569;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

/* Labels */
QLabel#Title {
    font-size: 32px;
    font-weight: bold;
    color: #f8fafc;
}

QLabel#Subtitle {
    font-size: 16px;
    color: #94a3b8;
}

/* Cards / Frames */
QFrame#Card {
    background-color: #1e293b;
    border-radius: 12px;
    border: 1px solid #334155;
}
"""
