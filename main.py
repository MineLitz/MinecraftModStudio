import sys
import os

# Ensure imports work from any directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from ui.theme import DARK_THEME
from ui.welcome_screen import WelcomeScreen
from ui.mainwindow import MainWindow


def main():
    # Enable high-DPI support
    os.environ.setdefault("QT_ENABLE_HIGHDPI_SCALING", "1")

    app = QApplication(sys.argv)
    app.setApplicationName("Minecraft Mod Studio")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("MMS")

    # Apply global dark theme
    app.setStyleSheet(DARK_THEME)

    # Default font
    font = QFont("Segoe UI", 10)
    app.setFont(font)

    main_window: MainWindow | None = None

    def open_main(workspace):
        nonlocal main_window
        welcome.hide()
        main_window = MainWindow(workspace)
        main_window.show()
        # Wire up save to update recent
        if workspace.file_path:
            _add_recent(workspace.file_path)

    def _add_recent(path: str):
        from PyQt6.QtCore import QSettings
        settings = QSettings("MMS", "MinecraftModStudio")
        recents = settings.value("recent_projects", []) or []
        if path in recents:
            recents.remove(path)
        recents.insert(0, path)
        settings.setValue("recent_projects", recents[:10])

    welcome = WelcomeScreen()
    welcome.open_main.connect(open_main)
    welcome.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
