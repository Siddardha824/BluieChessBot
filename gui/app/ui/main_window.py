from PySide6.QtWidgets import QMainWindow

from gui.utils.logger import get_logger

logger = get_logger(__name__)

class MainWindow(QMainWindow):
    def __init__(self, manager, parent = None):
        super().__init__(parent)

        self._manager = manager

        logger.info("Main window initialized")

        
