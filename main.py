import sys
from PyQt6.QtWidgets import QApplication
from gui.main_window import AudioSeparatorApp

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AudioSeparatorApp()
    window.show()
    sys.exit(app.exec())
