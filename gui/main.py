import sys
import traceback

from PySide6.QtWidgets import QApplication

from gui.ui import MainWindow
from gui.debug import get_logger

logger = get_logger(__name__)

def main():

    try:
        logger.info("Starting Bluie Chess GUI")

        app = QApplication(sys.argv)

        logger.info("Creating MainWindow")

        window = MainWindow()
        
        window.showMaximized()
        
        logger.info("Entering MainWindow event loop")

        sys.exit(app.exec())

    except Exception:
        traceback.print_exc()


if __name__ == "__main__":
    main()