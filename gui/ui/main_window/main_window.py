from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout
)

from gui.ui.board import ChessBoard
from gui.debug import get_logger

logger = get_logger(__name__)

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Bluie Chess")
        self.resize(1200, 700)

        self.setup_ui()

        logger.info("Main Window initialized")

    def setup_ui(self):

        container = QWidget()

        outer_layout = QVBoxLayout()

        middle_layout = QHBoxLayout()

        logger.info("Creating Chessboard widget")

        self.board = ChessBoard()

        middle_layout.addWidget(self.board)

        outer_layout.addLayout(middle_layout)

        container.setLayout(outer_layout)

        self.setCentralWidget(container)