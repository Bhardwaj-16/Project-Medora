import sys
import os

# Ensure the medora package directory is on the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtGui import QFont, QPalette, QColor
from xp_icons import icon_medora


def main():
    # Force standard desktop rendering to prevent macOS Dark Mode inversion
    os.environ["QT_MAC_WANTS_LAYER"] = "1"

    app = QApplication(sys.argv)
    app.setApplicationName("MEDORA")
    app.setOrganizationName("MEDORA Health Management")
    app.setApplicationVersion("1.2")
    app.setWindowIcon(icon_medora())

    # Use Fusion style as baseline to decouple from macOS Dark Mode theme clashes
    app.setStyle('Fusion')

    # Force a classic light palette so tooltips and text are always 100% visible
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor('#ECE9D8'))
    palette.setColor(QPalette.WindowText, QColor('#000000'))
    palette.setColor(QPalette.Base, QColor('#FFFFFF'))
    palette.setColor(QPalette.AlternateBase, QColor('#F1F6FC'))
    palette.setColor(QPalette.ToolTipBase, QColor('#FFFFE1'))
    palette.setColor(QPalette.ToolTipText, QColor('#000000'))
    palette.setColor(QPalette.Text, QColor('#000000'))
    palette.setColor(QPalette.Button, QColor('#ECE9D8'))
    palette.setColor(QPalette.ButtonText, QColor('#000000'))
    palette.setColor(QPalette.BrightText, QColor('#CC0000'))
    palette.setColor(QPalette.Highlight, QColor('#316AC5'))
    palette.setColor(QPalette.HighlightedText, QColor('#FFFFFF'))
    palette.setColor(QPalette.Disabled, QPalette.Text, QColor('#808080'))
    palette.setColor(QPalette.Disabled, QPalette.ButtonText, QColor('#808080'))
    app.setPalette(palette)

    # Set default classic Windows XP font (Tahoma / MS Sans Serif)
    font = QFont("Tahoma", 9)
    font.setStyleHint(QFont.SansSerif)
    app.setFont(font)

    # ── Setup Database ───────────────────────────────────────────────────────
    try:
        from db_setup import setup_database
        ok = setup_database()
        if not ok:
            QMessageBox.critical(
                None,
                "Database Error",
                "MEDORA could not connect to MySQL or set up the database.\n\n"
                "Please ensure:\n"
                "  1. MySQL server is running.\n"
                "  2. Credentials in db_setup.py are correct.\n\n"
                "Edit the db_config dict in db_setup.py and restart.",
            )
            sys.exit(1)
    except ConnectionError as e:
        QMessageBox.critical(
            None,
            "Database Connection Failed",
            f"Cannot connect to MySQL:\n\n{e}\n\n"
            "Please verify that MySQL is running and the credentials in\n"
            "db_setup.py (db_config) are correct, then restart MEDORA.",
        )
        sys.exit(1)
    except Exception as e:
        QMessageBox.critical(
            None,
            "Startup Error",
            f"An unexpected error occurred during startup:\n\n{e}",
        )
        sys.exit(1)

    # ── Show Login Window ────────────────────────────────────────────────────
    from login_window import LoginWindow
    win = LoginWindow()
    win.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
