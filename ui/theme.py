DARK_THEME = """
* {
    font-family: 'Inter', 'Segoe UI', 'Roboto', 'Open Sans', sans-serif;
    font-size: 12px;
    color: #d0d0d0;
}

QMainWindow, QDialog, QWidget {
    background-color: #252525;
}

QMenuBar {
    background-color: #1e1e1e;
    color: #b8b8b8;
    border-bottom: 1px solid #1a1a1a;
    padding: 1px 0;
}
QMenuBar::item { padding: 5px 10px; background: transparent; }
QMenuBar::item:selected { background-color: #383838; color: #e8e8e8; }
QMenu {
    background-color: #2c2c2c;
    border: 1px solid #1a1a1a;
    color: #c8c8c8;
    padding: 3px 0;
}
QMenu::item { padding: 6px 28px 6px 12px; }
QMenu::item:selected { background-color: #383838; color: #e8e8e8; }
QMenu::separator { height: 1px; background: #1e1e1e; margin: 3px 8px; }

QToolBar {
    background-color: #2c2c2c;
    border-bottom: 1px solid #1a1a1a;
    spacing: 3px;
    padding: 3px 8px;
}
QToolBar::separator { width: 1px; background: #1e1e1e; margin: 4px 3px; }
QToolButton {
    background-color: #383838;
    border: 1px solid #1e1e1e;
    border-radius: 4px;
    padding: 4px 11px;
    color: #c0c0c0;
}
QToolButton:hover { background-color: #424242; border-color: #505050; color: #e8e8e8; }
QToolButton:pressed { background-color: #2a2a2a; }
QToolButton#btn_new_element {
    background-color: #263320; border-color: #344828; color: #6ab84a; font-weight: 600;
}
QToolButton#btn_new_element:hover { background-color: #2e3e26; border-color: #4a6a34; color: #7ecc5e; }
QToolButton#btn_build { background-color: #302c22; border-color: #3c3420; color: #c89040; }
QToolButton#btn_build:hover { background-color: #3a3428; color: #daa84a; }
QToolButton#btn_export { background-color: #2a2c38; border-color: #303444; color: #6888c8; }
QToolButton#btn_export:hover { background-color: #303448; color: #80a0e0; }

QTreeWidget {
    background-color: #222222;
    border: none; outline: none;
    color: #b0b0b0;
    show-decoration-selected: 1;
}
QTreeWidget::item { padding: 4px; border: none; }
QTreeWidget::item:hover { background-color: #303030; color: #d0d0d0; }
QTreeWidget::item:selected { background-color: #2a3a28; color: #7ecc5e; }
QHeaderView::section {
    background-color: #222; color: #585858;
    border: none; border-bottom: 1px solid #1a1a1a;
    padding: 4px 8px; font-size: 10px;
}

QSplitter::handle { background-color: #1a1a1a; }
QSplitter::handle:horizontal { width: 1px; }
QSplitter::handle:vertical   { height: 1px; }

QScrollArea { border: none; background: transparent; }
QScrollBar:vertical {
    background: #1e1e1e; width: 7px; border: none; margin: 0;
}
QScrollBar::handle:vertical {
    background: #3a3a3a; border-radius: 3px; min-height: 24px;
}
QScrollBar::handle:vertical:hover { background: #4a4a4a; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QScrollBar:horizontal { background: #1e1e1e; height: 7px; border: none; }
QScrollBar::handle:horizontal { background: #3a3a3a; border-radius: 3px; min-width: 24px; }
QScrollBar::handle:horizontal:hover { background: #4a4a4a; }
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; }

QPushButton {
    background-color: #383838; border: 1px solid #1e1e1e;
    border-radius: 4px; padding: 6px 16px; color: #c8c8c8;
}
QPushButton:hover { background-color: #424242; border-color: #505050; color: #e8e8e8; }
QPushButton:pressed { background-color: #2e2e2e; }
QPushButton:disabled { background-color: #2a2a2a; color: #505050; border-color: #1e1e1e; }
QPushButton#btn_primary {
    background-color: #263320; border-color: #3a5028;
    color: #6ab84a; font-weight: 600; font-size: 13px; padding: 9px 24px;
}
QPushButton#btn_primary:hover { background-color: #2e3e26; border-color: #4e6a38; color: #82cc60; }
QPushButton#btn_secondary {
    background-color: #303030; border-color: #1e1e1e;
    color: #909090; font-size: 13px; padding: 9px 24px;
}
QPushButton#btn_secondary:hover { background-color: #3a3a3a; color: #c0c0c0; }
QPushButton#btn_danger { background-color: #301e1e; border-color: #481e1e; color: #c04040; }
QPushButton#btn_danger:hover { background-color: #3a2222; color: #e05050; }

QLineEdit {
    background-color: #1e1e1e; border: 1px solid #383838;
    border-radius: 4px; padding: 5px 8px; color: #d0d0d0;
    selection-background-color: #344828;
}
QLineEdit:focus { border-color: #4a6a38; background-color: #202020; }
QLineEdit:hover { border-color: #484848; }

QTextEdit, QPlainTextEdit {
    background-color: #1a1a1a; border: none;
    color: #606a58; font-family: 'Consolas', monospace; font-size: 11px; padding: 6px;
}

QComboBox {
    background-color: #1e1e1e; border: 1px solid #383838;
    border-radius: 4px; padding: 5px 8px; color: #c8c8c8; min-width: 80px;
}
QComboBox:hover { border-color: #484848; }
QComboBox:focus { border-color: #4a6a38; }
QComboBox::drop-down { border: none; width: 20px; }
QComboBox::down-arrow {
    image: none;
    border-left: 4px solid transparent; border-right: 4px solid transparent;
    border-top: 5px solid #606060; width: 0; height: 0; margin-right: 6px;
}
QComboBox QAbstractItemView {
    background-color: #2c2c2c; border: 1px solid #1a1a1a;
    selection-background-color: #2a3a28; selection-color: #7ecc5e; outline: none;
}

QSpinBox, QDoubleSpinBox {
    background-color: #1e1e1e; border: 1px solid #383838;
    border-radius: 4px; padding: 5px 8px; color: #c8c8c8;
}
QSpinBox:focus, QDoubleSpinBox:focus { border-color: #4a6a38; }
QSpinBox::up-button, QSpinBox::down-button,
QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {
    background-color: #303030; border: none; width: 16px;
}
QSpinBox::up-button:hover, QSpinBox::down-button:hover,
QDoubleSpinBox::up-button:hover, QDoubleSpinBox::down-button:hover {
    background-color: #404040;
}

QCheckBox { color: #b0b0b0; spacing: 7px; }
QCheckBox::indicator {
    width: 14px; height: 14px; border-radius: 3px;
    border: 1px solid #484848; background-color: #1e1e1e;
}
QCheckBox::indicator:checked { background-color: #3a5a28; border-color: #4a7a30; }
QCheckBox::indicator:hover { border-color: #585858; }

QTabWidget::pane { border: none; background-color: #222222; }
QTabBar::tab {
    background-color: #252525; color: #686868;
    padding: 6px 16px; border-right: 1px solid #1a1a1a; font-size: 11px; min-width: 60px;
}
QTabBar::tab:selected { background-color: #222222; color: #c8c8c8; border-top: 2px solid #5a9a38; }
QTabBar::tab:hover:!selected { background-color: #2c2c2c; color: #a0a0a0; }

QLabel { background: transparent; color: #c0c0c0; }

QGroupBox {
    border: 1px solid #2c2c2c; border-radius: 4px;
    margin-top: 8px; padding-top: 10px; color: #606060; font-size: 10px;
}
QGroupBox::title { subcontrol-origin: margin; left: 8px; padding: 0 4px; }

QStatusBar {
    background-color: #1a1a1a; color: #6ab84a;
    font-size: 11px; border-top: 1px solid #141414;
}
QStatusBar::item { border: none; }

QToolTip {
    background-color: #2c2c2c; color: #c8c8c8;
    border: 1px solid #1a1a1a; border-radius: 4px; padding: 5px 8px; font-size: 11px;
}

QDialog { background-color: #282828; }
QMessageBox { background-color: #282828; }
QMessageBox QLabel { color: #c0c0c0; font-size: 12px; }
"""


LIGHT_THEME = """
* {
    font-family: 'Inter', 'Segoe UI', 'Roboto', 'Open Sans', sans-serif;
    font-size: 12px;
    color: #1a1a1a;
}
QMainWindow, QDialog, QWidget { background-color: #f0f0f0; }
QMenuBar { background-color: #e0e0e0; color: #1a1a1a; border-bottom: 1px solid #c0c0c0; padding: 1px 0; }
QMenuBar::item { padding: 5px 10px; background: transparent; }
QMenuBar::item:selected { background-color: #d0d0d0; color: #000; }
QMenu { background-color: #f5f5f5; border: 1px solid #c0c0c0; color: #1a1a1a; padding: 3px 0; }
QMenu::item { padding: 6px 28px 6px 12px; }
QMenu::item:selected { background-color: #e0e0e0; }
QMenu::separator { height: 1px; background: #d0d0d0; margin: 3px 8px; }
QToolBar { background-color: #e8e8e8; border-bottom: 1px solid #c0c0c0; spacing: 3px; padding: 3px 8px; }
QToolBar::separator { width: 1px; background: #c8c8c8; margin: 4px 3px; }
QToolButton { background-color: #dcdcdc; border: 1px solid #c0c0c0; border-radius: 4px; padding: 4px 11px; color: #1a1a1a; }
QToolButton:hover { background-color: #d0d0d0; border-color: #a0a0a0; }
QToolButton:pressed { background-color: #c8c8c8; }
QToolButton#btn_new_element { background-color: #d0ead0; border-color: #5a9a38; color: #2a6010; font-weight: 600; }
QToolButton#btn_new_element:hover { background-color: #c0e0c0; }
QToolButton#btn_build { background-color: #ead8b0; border-color: #a07820; color: #5a4010; }
QToolButton#btn_export { background-color: #c8d4f0; border-color: #4860a0; color: #203060; }
QTreeWidget { background-color: #f8f8f8; border: none; outline: none; color: #1a1a1a; }
QTreeWidget::item { padding: 4px; border: none; }
QTreeWidget::item:hover { background-color: #e8e8e8; }
QTreeWidget::item:selected { background-color: #c8e0c8; color: #204010; }
QSplitter::handle { background-color: #c8c8c8; }
QSplitter::handle:horizontal { width: 1px; }
QScrollBar:vertical { background: #f0f0f0; width: 7px; border: none; }
QScrollBar::handle:vertical { background: #c0c0c0; border-radius: 3px; min-height: 24px; }
QScrollBar::handle:vertical:hover { background: #a8a8a8; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QScrollBar:horizontal { background: #f0f0f0; height: 7px; border: none; }
QScrollBar::handle:horizontal { background: #c0c0c0; border-radius: 3px; min-width: 24px; }
QPushButton { background-color: #dcdcdc; border: 1px solid #c0c0c0; border-radius: 4px; padding: 6px 16px; color: #1a1a1a; }
QPushButton:hover { background-color: #d0d0d0; border-color: #a0a0a0; }
QPushButton:pressed { background-color: #c8c8c8; }
QPushButton:disabled { background-color: #e8e8e8; color: #a0a0a0; border-color: #d0d0d0; }
QPushButton#btn_primary { background-color: #d0ead0; border-color: #5a9a38; color: #2a6010; font-weight: 600; font-size: 13px; padding: 9px 24px; }
QPushButton#btn_primary:hover { background-color: #c0e0c0; border-color: #4a8a28; }
QPushButton#btn_secondary { background-color: #e0e0e0; border-color: #c0c0c0; color: #505050; font-size: 13px; padding: 9px 24px; }
QPushButton#btn_danger { background-color: #f0d0d0; border-color: #c04040; color: #802020; }
QLineEdit { background-color: #ffffff; border: 1px solid #c0c0c0; border-radius: 4px; padding: 5px 8px; color: #1a1a1a; selection-background-color: #c8e0c8; }
QLineEdit:focus { border-color: #5a9a38; }
QLineEdit:hover { border-color: #a0a0a0; }
QTextEdit, QPlainTextEdit { background-color: #f8f8f8; border: none; color: #303a28; font-family: 'Consolas', monospace; font-size: 11px; padding: 6px; }
QComboBox { background-color: #ffffff; border: 1px solid #c0c0c0; border-radius: 4px; padding: 5px 8px; color: #1a1a1a; min-width: 80px; }
QComboBox:hover { border-color: #a0a0a0; }
QComboBox:focus { border-color: #5a9a38; }
QComboBox::drop-down { border: none; width: 20px; }
QComboBox::down-arrow { image: none; border-left: 4px solid transparent; border-right: 4px solid transparent; border-top: 5px solid #808080; width: 0; height: 0; margin-right: 6px; }
QComboBox QAbstractItemView { background-color: #ffffff; border: 1px solid #c0c0c0; selection-background-color: #c8e0c8; selection-color: #204010; outline: none; }
QSpinBox, QDoubleSpinBox { background-color: #ffffff; border: 1px solid #c0c0c0; border-radius: 4px; padding: 5px 8px; color: #1a1a1a; }
QSpinBox:focus, QDoubleSpinBox:focus { border-color: #5a9a38; }
QSpinBox::up-button, QSpinBox::down-button, QDoubleSpinBox::up-button, QDoubleSpinBox::down-button { background-color: #e8e8e8; border: none; width: 16px; }
QCheckBox { color: #1a1a1a; spacing: 7px; }
QCheckBox::indicator { width: 14px; height: 14px; border-radius: 3px; border: 1px solid #c0c0c0; background-color: #ffffff; }
QCheckBox::indicator:checked { background-color: #5a9a38; border-color: #4a8a28; }
QTabWidget::pane { border: none; background-color: #f0f0f0; }
QTabBar::tab { background-color: #e0e0e0; color: #606060; padding: 6px 16px; border-right: 1px solid #c8c8c8; font-size: 11px; }
QTabBar::tab:selected { background-color: #f0f0f0; color: #1a1a1a; border-top: 2px solid #5a9a38; }
QTabBar::tab:hover:!selected { background-color: #d8d8d8; }
QLabel { background: transparent; color: #1a1a1a; }
QGroupBox { border: 1px solid #c8c8c8; border-radius: 4px; margin-top: 8px; padding-top: 10px; color: #606060; font-size: 10px; }
QStatusBar { background-color: #d0e8c8; color: #2a6010; font-size: 11px; border-top: 1px solid #b0d0a0; }
QStatusBar::item { border: none; }
QToolTip { background-color: #f0f0f0; color: #1a1a1a; border: 1px solid #c0c0c0; border-radius: 4px; padding: 5px 8px; font-size: 11px; }
QDialog { background-color: #f0f0f0; }
QMessageBox { background-color: #f0f0f0; }
QMessageBox QLabel { color: #1a1a1a; font-size: 12px; }
"""

FONT_SIZES = {
    "small":  "11px",
    "medium": "12px",
    "large":  "14px",
}

def build_theme(theme: str = "dark", font_name: str = "Inter", font_size: str = "medium") -> str:
    base = DARK_THEME if theme == "dark" else LIGHT_THEME
    size = FONT_SIZES.get(font_size, "12px")
    result = base.replace(
        "'Inter', 'Segoe UI', 'Roboto', 'Open Sans', sans-serif",
        f"'{font_name}', 'Segoe UI', sans-serif"
    )
    result = result.replace("font-size: 12px;", f"font-size: {size};", 1)
    return result
