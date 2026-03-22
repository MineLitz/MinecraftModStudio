DARK_THEME = """
QMainWindow, QDialog {
    background-color: #1e1e1e;
    color: #cccccc;
}

QWidget {
    background-color: #1e1e1e;
    color: #cccccc;
    font-family: 'Segoe UI', Arial;
    font-size: 12px;
}

/* ── MENU BAR ── */
QMenuBar {
    background-color: #252525;
    color: #cccccc;
    border-bottom: 1px solid #333;
    padding: 2px 0;
}
QMenuBar::item {
    padding: 4px 10px;
    border-radius: 3px;
}
QMenuBar::item:selected {
    background-color: #333;
    color: #ffffff;
}
QMenu {
    background-color: #2a2a2a;
    border: 1px solid #3a3a3a;
    color: #cccccc;
    padding: 4px 0;
}
QMenu::item {
    padding: 6px 20px 6px 10px;
}
QMenu::item:selected {
    background-color: #2a4a1a;
    color: #7ec850;
}
QMenu::separator {
    height: 1px;
    background: #3a3a3a;
    margin: 4px 8px;
}

/* ── TOOLBAR ── */
QToolBar {
    background-color: #252525;
    border-bottom: 1px solid #333;
    spacing: 4px;
    padding: 4px 8px;
}
QToolBar::separator {
    width: 1px;
    background: #3a3a3a;
    margin: 3px 4px;
}
QToolButton {
    background-color: #333;
    border: 1px solid #444;
    border-radius: 4px;
    padding: 4px 10px;
    color: #cccccc;
    font-size: 12px;
}
QToolButton:hover {
    background-color: #3d3d3d;
    border-color: #555;
    color: #ffffff;
}
QToolButton:pressed {
    background-color: #2a2a2a;
}
QToolButton#btn_new_element {
    background-color: #1e3a10;
    border-color: #4a8a20;
    color: #7ec850;
    font-weight: bold;
}
QToolButton#btn_new_element:hover {
    background-color: #2a5018;
    border-color: #6aaa30;
}
QToolButton#btn_build, QToolButton#btn_export {
    background-color: #3a2a0a;
    border-color: #7a5a1a;
    color: #f0a020;
}
QToolButton#btn_build:hover, QToolButton#btn_export:hover {
    background-color: #4a3a10;
    border-color: #9a7a2a;
}

/* ── TREE WIDGET ── */
QTreeWidget {
    background-color: #1a1a1a;
    border: none;
    outline: none;
    color: #bbbbbb;
}
QTreeWidget::item {
    padding: 4px 4px;
    border-radius: 3px;
}
QTreeWidget::item:hover {
    background-color: #2a2a2a;
    color: #dddddd;
}
QTreeWidget::item:selected {
    background-color: #1a3010;
    color: #7ec850;
}
QTreeWidget::branch {
    background: transparent;
}
QTreeWidget::branch:has-children:!has-siblings:closed,
QTreeWidget::branch:closed:has-children:has-siblings {
    image: none;
}
QHeaderView {
    background-color: #1a1a1a;
}
QHeaderView::section {
    background-color: #222;
    color: #666;
    border: none;
    padding: 4px 8px;
    font-size: 10px;
    text-transform: uppercase;
    letter-spacing: 1px;
}

/* ── SPLITTER ── */
QSplitter::handle {
    background-color: #333;
}
QSplitter::handle:horizontal {
    width: 1px;
}

/* ── SCROLL AREA ── */
QScrollArea {
    border: none;
    background-color: #181818;
}
QScrollBar:vertical {
    background: #1e1e1e;
    width: 8px;
    border: none;
}
QScrollBar::handle:vertical {
    background: #3a3a3a;
    border-radius: 4px;
    min-height: 30px;
}
QScrollBar::handle:vertical:hover {
    background: #4a4a4a;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
QScrollBar:horizontal {
    background: #1e1e1e;
    height: 8px;
    border: none;
}
QScrollBar::handle:horizontal {
    background: #3a3a3a;
    border-radius: 4px;
    min-width: 30px;
}

/* ── BUTTONS ── */
QPushButton {
    background-color: #333;
    border: 1px solid #444;
    border-radius: 5px;
    padding: 7px 16px;
    color: #cccccc;
    font-size: 12px;
}
QPushButton:hover {
    background-color: #3d3d3d;
    border-color: #555;
    color: #ffffff;
}
QPushButton:pressed {
    background-color: #2a2a2a;
}
QPushButton#btn_primary {
    background-color: #1e4a10;
    border-color: #4a8a20;
    color: #7ec850;
    font-weight: bold;
    font-size: 13px;
    padding: 10px 24px;
}
QPushButton#btn_primary:hover {
    background-color: #285c16;
    border-color: #6aaa30;
    color: #9adc60;
}
QPushButton#btn_secondary {
    background-color: #2a2a2a;
    border-color: #555;
    color: #aaaaaa;
    padding: 10px 24px;
    font-size: 13px;
}
QPushButton#btn_secondary:hover {
    background-color: #333;
    color: #cccccc;
}
QPushButton#btn_danger {
    background-color: #3a1010;
    border-color: #7a2020;
    color: #e04040;
}
QPushButton#btn_danger:hover {
    background-color: #4a1818;
    border-color: #9a3030;
}

/* ── INPUTS ── */
QLineEdit {
    background-color: #2a2a2a;
    border: 1px solid #444;
    border-radius: 4px;
    padding: 5px 8px;
    color: #cccccc;
    selection-background-color: #2a5018;
}
QLineEdit:focus {
    border-color: #4a8a20;
    background-color: #252525;
}
QLineEdit:hover {
    border-color: #555;
}
QTextEdit, QPlainTextEdit {
    background-color: #141414;
    border: none;
    color: #8a9a7a;
    font-family: 'Consolas', monospace;
    font-size: 11px;
    padding: 6px;
}
QComboBox {
    background-color: #2a2a2a;
    border: 1px solid #444;
    border-radius: 4px;
    padding: 5px 8px;
    color: #cccccc;
    min-width: 80px;
}
QComboBox:hover { border-color: #555; }
QComboBox:focus { border-color: #4a8a20; }
QComboBox::drop-down {
    border: none;
    width: 20px;
}
QComboBox::down-arrow {
    image: none;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 6px solid #666;
    width: 0;
    height: 0;
    margin-right: 6px;
}
QComboBox QAbstractItemView {
    background-color: #2a2a2a;
    border: 1px solid #444;
    selection-background-color: #2a4a1a;
    selection-color: #7ec850;
}
QSpinBox, QDoubleSpinBox {
    background-color: #2a2a2a;
    border: 1px solid #444;
    border-radius: 4px;
    padding: 5px 8px;
    color: #cccccc;
}
QSpinBox:focus, QDoubleSpinBox:focus { border-color: #4a8a20; }
QSpinBox::up-button, QSpinBox::down-button,
QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {
    background-color: #333;
    border: none;
    width: 16px;
}
QCheckBox {
    color: #bbbbbb;
    spacing: 6px;
}
QCheckBox::indicator {
    width: 15px;
    height: 15px;
    border-radius: 3px;
    border: 1px solid #555;
    background-color: #2a2a2a;
}
QCheckBox::indicator:checked {
    background-color: #3a7a20;
    border-color: #5aaa30;
}

/* ── TABS ── */
QTabWidget::pane {
    border: none;
    background-color: #181818;
}
QTabBar::tab {
    background-color: #222;
    color: #777;
    padding: 6px 14px;
    border-right: 1px solid #333;
    font-size: 11px;
}
QTabBar::tab:selected {
    background-color: #181818;
    color: #cccccc;
    border-top: 2px solid #7ec850;
}
QTabBar::tab:hover {
    background-color: #2a2a2a;
    color: #aaaaaa;
}
QTabBar::close-button {
    image: none;
}

/* ── LABELS ── */
QLabel {
    color: #cccccc;
    background: transparent;
}
QLabel#label_section {
    color: #666;
    font-size: 10px;
    text-transform: uppercase;
    letter-spacing: 1px;
}
QLabel#label_title {
    color: #7ec850;
    font-size: 18px;
    font-weight: bold;
}
QLabel#label_muted {
    color: #666;
    font-size: 11px;
}

/* ── STATUS BAR ── */
QStatusBar {
    background-color: #1a3010;
    color: #7ec850;
    font-size: 11px;
    border-top: 1px solid #2a5018;
    padding: 0 8px;
}
QStatusBar::item {
    border: none;
}

/* ── FRAME ── */
QFrame#panel_frame {
    background-color: #1e1e1e;
    border: none;
}
QFrame#separator {
    background-color: #333;
    max-width: 1px;
}

/* ── GROUP BOX ── */
QGroupBox {
    border: 1px solid #333;
    border-radius: 5px;
    margin-top: 8px;
    padding-top: 10px;
    color: #888;
    font-size: 10px;
    text-transform: uppercase;
    letter-spacing: 1px;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 8px;
    padding: 0 4px;
    color: #666;
    font-size: 10px;
}

/* ── TOOLTIPS ── */
QToolTip {
    background-color: #2a2a2a;
    color: #cccccc;
    border: 1px solid #444;
    border-radius: 4px;
    padding: 5px 8px;
    font-size: 11px;
}
"""
