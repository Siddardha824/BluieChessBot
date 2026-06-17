from PySide6.QtWidgets import QVBoxLayout

from ..templates import StyledWidget
from ..panels import Chessboard

class HomePage(StyledWidget):
    def __init__(self, app_manager, parent = None):
        super().__init__("homePage", parent)

        self.manager = app_manager

        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        self.board = Chessboard(self.manager, self)
        layout.addWidget(self.board)

