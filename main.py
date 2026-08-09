"""
Fhish's View — Premium Windows desktop overlay
Your Windows. Reimagined.
"""

import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from src.island_window import IslandWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Fhish's View")
    app.setQuitOnLastWindowClosed(True)

    window = IslandWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
