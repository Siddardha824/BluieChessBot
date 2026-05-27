# gui/main_window.py

from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout
from gui.board.board_widget import ChessBoard
from gui.controllers.game_controller import GameController
from gui.utils.logger import get_logger

logger = get_logger(__name__)

class MainWindow(QMainWindow):
    def __init__(self):
        """
        Initializes the primary MainWindow layout.
        Acts as the central coordination container connecting widgets and controllers.
        """
        super().__init__()

        self.setWindowTitle("Bluie Chess")
        self.resize(1200, 700)

        # 1. Instantiate the State Controller
        self.game_controller = GameController(self)

        # 2. Setup layouts & inject models
        self.setup_ui()
        
        # 3. Wire Signals and Slots
        self.wire_connections()
        
        logger.info("MainWindow UI framework successfully bootstrapped.")

    def setup_ui(self) -> None:
        """
        Creates layout structures and instantiates view components, 
        injecting the controller's state models directly.
        """
        container = QWidget()
        
        outer_layout = QVBoxLayout()
        outer_layout.setContentsMargins(10, 10, 10, 10)
        
        middle_layout = QHBoxLayout()
        
        logger.info("Instantiating ChessBoard widget within MainWindow layout.")
        self.board = ChessBoard()
        
        # Inject state models from controller directly into Board view
        self.board.set_models(
            self.game_controller.board_state,
            self.game_controller.highlight_manager
        )
        
        middle_layout.addWidget(self.board)
        outer_layout.addLayout(middle_layout)
        container.setLayout(outer_layout)
        
        self.setCentralWidget(container)

    def wire_connections(self) -> None:
        """
        Locks in uni-directional events using Qt Signals & Slots.
        """
        # Connect clicking event from BoardWidget to Controller slot
        self.board.square_clicked.connect(self.game_controller.handle_square_clicked)
        
        # Connect state change signals from Controller to trigger BoardWidget repaints
        self.game_controller.state_changed.connect(self.board.update)
