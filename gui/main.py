# gui/main.py

import sys
import traceback
from PySide6.QtWidgets import QApplication

from gui.main_window import MainWindow
from gui.utils.logger import get_logger

logger = get_logger(__name__)

def main():
    """
    Bootstrap entry point for Bluie Chess Bot UI.
    Initializes standard Qt applications and launches active MainWindow loops.
    """
    try:
        logger.info("Starting Bluie Chess GUI")

        # Initialize the global Qt application
        app = QApplication(sys.argv)

        logger.info("Creating MainWindow")
        window = MainWindow()
        
        # Maximize the window for a premium tournament experience
        window.showMaximized()
        
        logger.info("Entering MainWindow event loop")
        sys.exit(app.exec())

    except Exception as e:
        logger.exception("An unhandled exception occurred during application execution")
        traceback.print_exc()

if __name__ == "__main__":
    main()