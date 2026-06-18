from PySide6.QtWidgets import QHBoxLayout

from ..templates import StyledWidget
from ..panels import Chessboard, ControlPanel

class HomePage(StyledWidget):
    def __init__(self, app_manager, parent = None):
        super().__init__("homePage", parent)

        self.manager = app_manager

        self.setup_ui()

    def setup_ui(self):
        layout = QHBoxLayout(self)
        self.board = Chessboard(self.manager, self)
        self.control_panel = ControlPanel(self.manager, self)
        layout.addWidget(self.board, stretch=3)
        layout.addWidget(self.control_panel, stretch=1)

