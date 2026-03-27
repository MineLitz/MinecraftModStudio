import sys
import os
import traceback

# Ensure imports work from any directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import core.logger as log

from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from ui.theme import DARK_THEME
from ui.welcome_screen import WelcomeScreen
from ui.mainwindow import MainWindow
from ui.font_loader import load_fonts


def _install_exception_hook(app: QApplication):
    """
    Installs a global exception hook that:
    1. Logs the full traceback to resources/logs/mms.log
    2. Shows a crash dialog with the error + log path
    3. Keeps the app alive instead of silently crashing
    """
    def hook(exc_type, exc_value, exc_tb):
        tb_str = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))

        # Log it
        log.critical("=" * 60)
        log.critical("UNHANDLED EXCEPTION — app did not crash silently")
        log.critical(tb_str)
        log.critical("=" * 60)

        # Also print to stderr (visible in run.bat cmd window)
        print("\n" + "=" * 60, file=sys.stderr)
        print("ERRO NÃO TRATADO:", file=sys.stderr)
        print(tb_str, file=sys.stderr)
        print("Log salvo em:", log.get_log_path(), file=sys.stderr)
        print("=" * 60, file=sys.stderr)

        # Show dialog (only if QApplication is running)
        try:
            msg = QMessageBox()
            msg.setWindowTitle("Erro — Minecraft Mod Studio")
            msg.setIcon(QMessageBox.Icon.Critical)
            msg.setText(f"<b>Ocorreu um erro inesperado:</b><br><br>"
                        f"<code>{exc_type.__name__}: {exc_value}</code>")
            msg.setDetailedText(tb_str)
            msg.setInformativeText(
                f"O erro foi salvo em:\n{log.get_log_path()}\n\n"
                "O app tentará continuar. Se travar, reinicie.")
            msg.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg.exec()
        except Exception:
            pass  # if dialog itself fails, at least the log was written

    sys.excepthook = hook

    # Also catch exceptions thrown inside Qt slots (they bypass sys.excepthook)
    import PyQt6.QtCore as QtCore
    old_excepthook = sys.excepthook
    def qt_message_handler(mode, context, message):
        if "Exception" in message or "Error" in message:
            log.error(f"Qt message [{mode}]: {message}")
    QtCore.qInstallMessageHandler(qt_message_handler)


def main():
    os.environ.setdefault("QT_ENABLE_HIGHDPI_SCALING", "1")

    app = QApplication(sys.argv)
    app.setApplicationName("Minecraft Mod Studio")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("MMS")

    # Install global exception hook ASAP
    _install_exception_hook(app)

    font_name = load_fonts()
    theme = DARK_THEME.replace(
        "'Inter', 'Segoe UI', 'Roboto', 'Open Sans', sans-serif",
        f"'{font_name}', sans-serif"
    )
    app.setStyleSheet(theme)

    font = QFont(font_name, 10)
    app.setFont(font)

    icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             "resources", "icons", "logo.png")
    if os.path.exists(icon_path):
        from PyQt6.QtGui import QIcon
        app.setWindowIcon(QIcon(icon_path))

    log.info(f"App started — Python {sys.version.split()[0]}")

    main_window: MainWindow | None = None

    def open_main(workspace):
        nonlocal main_window
        try:
            welcome.hide()
            main_window = MainWindow(workspace)

            def on_return_to_welcome():
                main_window.hide()
                welcome._populate_recent()
                welcome.show()

            main_window.return_to_welcome.connect(on_return_to_welcome)
            main_window.show()
            if workspace.file_path:
                _add_recent(workspace.file_path)
            log.info(f"MainWindow opened for project: {workspace.project_name or '(new)'}")
        except Exception:
            log.exception("Failed to open MainWindow")
            raise

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
    try:
        main()
    except SystemExit:
        pass  # normal exit
    except Exception:
        log.exception("Fatal error in main()")
        print("\nFatal error — see log:", log.get_log_path(), file=sys.stderr)
