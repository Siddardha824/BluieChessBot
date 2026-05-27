# gui/main_window.py

from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout
from gui.board.board_widget import ChessBoard
from gui.utils.logger import get_logger

logger = get_logger(__name__)

class MainWindow(QMainWindow):
    def __init__(self):
        """
        Initializes the primary MainWindow layout.
        Acts as a shell container for sub-widgets.
        """
        super().__init__()

        self.setWindowTitle("Bluie Chess")
        self.resize(1200, 700)

        self.setup_ui()
        logger.info("MainWindow UI framework successfully bootstrapped.")

    def setup_ui(self) -> None:
        """
        Creates outer layouts and instantiates the main board widget.
        """
        container = QWidget()
        
        # Outer vertical layout (allows margins, headers, or status bars)
        outer_layout = QVBoxLayout()
        outer_layout.setContentsMargins(10, 10, 10, 10)
        
        # Horizontal layout to host the chessboard alongside sidebar components later
        middle_layout = QHBoxLayout()
        
        logger.info("Instantiating ChessBoard widget within MainWindow layout.")
        self.board = ChessBoard()
        
        middle_layout.addWidget(self.board)
        
        outer_layout.addLayout(middle_layout)
        container.setLayout(outer_layout)
        
        self.setCentralWidget(container)
