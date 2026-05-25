import sys
from PySide6.QtWidgets import QApplication
from gui.ui import MainWindow

def main():
    """
    Main startup function. Initializes the QApplication, applies stylesheets,
    loads the dashboard MainWindow, and starts the event loop.
    """

    app = QApplication(sys.argv)

    main_window = MainWindow()

    main_window.showMaximized()

    sys.exit(app.exec())

    
if __name__ == "__main__":
    main()
