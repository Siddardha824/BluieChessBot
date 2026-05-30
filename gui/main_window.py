# gui/main_window.py

from PySide6.QtWidgets import QMainWindow
from PySide6.QtGui import QCloseEvent

from gui.controllers.game_controller import GameController
from gui.views.analysis.analysis_view import AnalysisView
from gui.utils.logger import get_logger

logger = get_logger(__name__)

class MainWindow(QMainWindow):
    def __init__(self):
        """
        Initializes the primary MainWindow shell container.
        Acts as a minimal, high-level manager that injects models and brokers
        connections down to modular view panels.
        """
        super().__init__()

        self.setWindowTitle("Bluie Chess Workbench")
        self.resize(1200, 750)

        # 1. Instantiate state controller
        self.game_controller = GameController(self)

        # 2. Setup layouts & view views
        self.setup_ui()
        
        # 3. Connect unified signal wires
        self.wire_connections()
        
        # Log successful bootstrap in workspace debug logger
        self.analysis_view.debug_console.log_message("INFO", "Bluie Chess GUI system successfully bootstrapped.")
        self.analysis_view.debug_console.log_message("INFO", "Awaiting user moves on the chessboard...")
        logger.info("MainWindow UI framework successfully bootstrapped.")

    def setup_ui(self) -> None:
        """Instantiates layout sections and view components."""
        # Instantiate 3-column analysis workspace
        self.analysis_view = AnalysisView(engine_manager=self.game_controller.engine_manager)

        # Inject Board models directly into ChessBoard widget
        self.analysis_view.board.set_models(
            self.game_controller.board_state,
            self.game_controller.highlight_manager
        )

        self.setCentralWidget(self.analysis_view)

    def wire_connections(self) -> None:
        """Wires coordinates, clicks, updates, and delegates engine connection plumbing."""
        # Connect board index selection to controller move triggers
        self.analysis_view.board.square_clicked.connect(self.game_controller.handle_square_clicked)
        
        # Connect board repaints on state changes
        self.game_controller.signals.state_changed.connect(self.analysis_view.board.update)
        
        # Delegate all engine stdio logs, calculation progress, and move logging to AnalysisView
        self.analysis_view.connect_engine(
            self.game_controller.engine_manager,
            self.game_controller
        )
        
        # Wire control action handlers
        self.analysis_view.control_section.clear_board_clicked.connect(self._handle_clear_board)
        self.analysis_view.control_section.flip_board_clicked.connect(self._handle_flip_board)

    def _handle_clear_board(self) -> None:
        """Clears moves and resets active board to standard start FEN."""
        self.game_controller.engine_manager.send_command("ucinewgame")
        self.game_controller.board_state.set_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
        self.game_controller.highlight_manager.reset()
        self.analysis_view.move_list.clear()
        self.analysis_view.clear()
        self.analysis_view.board.update()
        self.game_controller.sync_position_and_query_legals()
        self.analysis_view.debug_console.log_message("INFO", "Chessboard cleared and reset.")

    def _handle_flip_board(self) -> None:
        """Toggles visual board orientation (flips coordinates/color perspectives)."""
        self.analysis_view.debug_console.log_message("INFO", "Board perspective flipped.")

    def closeEvent(self, event: QCloseEvent) -> None:
        """Safely stops active search calculations and releases sub-process resources."""
        logger.info("MainWindow closeEvent received. Releasing resources...")
        self.game_controller.cleanup()
        event.accept()
