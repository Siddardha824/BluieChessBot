from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QWidget
from typing import TYPE_CHECKING

from .pages import HomePage
from gui.utils.logger import get_logger
if TYPE_CHECKING:
    from gui.app.app_manager import AppManager

logger = get_logger(__name__)

class MainWindow(QMainWindow):
    def __init__(self, manager: "AppManager"):
        super().__init__()
        self.setObjectName("mainWindow")
        self.setWindowTitle("Bluie Chess")
        self.resize(1200, 750)

        self._manager = manager

        logger.info("Setting up UI")
        self.setup_ui()

    @property
    def manager(self) -> "AppManager":
        return self._manager

    def setup_ui(self) -> None:
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        layout = QVBoxLayout(self.central_widget)

        self.home_page = HomePage(self.manager, self.central_widget)
        self.home_page.setObjectName("homePage")

        layout.addWidget(self.home_page)

        self.manager.set_theme()

    def closeEvent(self, event: QCloseEvent) -> None:
        logger.info("MainWindow close event triggered, shutting down services")
        self.manager.shutdown()
        event.accept()



