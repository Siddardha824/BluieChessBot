# gui/controllers/game_controller.py

import os
from PySide6.QtCore import QObject, QTimer
from gui.utils.logger import get_logger

from gui.controllers.board_controller import BoardController
from gui.controllers.handlers.engine_handler import EngineHandler
from gui.controllers.handlers.overlay_handler import OverlayHandler

from gui.engine.engine_manager import EngineManager

logger = get_logger(__name__)

class GameController:
    def __init__(self, parent: QObject | None = None):
        """
        Orchestrator connecting decoupled sub-controllers and engine handlers.
        Converts GameController to a pure Python class to protect Turn evaluations
        and coordinate highlights from Shiboken C++ marshalling errors.
        """
        # 1. Instantiate the BoardController that owns the models
        self.board_controller = BoardController()
        
        # Expose board state models directly for view rendering injection
        self.board_state = self.board_controller.board_state
        self.highlight_manager = self.board_controller.highlight_manager
        
        # Forward signals reference for backwards compatibility
        self.signals = self.board_controller
        
        # 2. Instantiate the EngineManager, using board_controller as the Qt parent context
        self.engine_manager = EngineManager(self.board_controller)
        
        # 3. Instantiate highly focused handlers
        self.engine_handler = EngineHandler(self.engine_manager, self.board_state)
        self.overlay_handler = OverlayHandler(self.engine_manager, self.board_state, self.highlight_manager)
        
        # 4. Resolve compiled C++ engine path
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
        self.engine_path = os.path.join(project_root, "build", "BluieChessBot.exe")
        
        # Wire interactive events across sub-controllers dynamically
        self._wire_controller_events()
        
        # 5. Boot engine subprocess
        if os.path.exists(self.engine_path):
            self.engine_manager.start_engine(self.engine_path)
            def on_startup_ready():
                self.engine_handler.send_engine_options()
                self.engine_handler.sync_position_and_query_legals()
            QTimer.singleShot(800, on_startup_ready)
        else:
            logger.warning(f"Engine executable not found at startup: {self.engine_path}. Awaiting manual launch.")
            
        logger.info("GameController successfully initialized in modular architecture.")

    def _wire_controller_events(self) -> None:
        """Wires coordinates and events across components dynamically."""
        # A. Bind Engine completions to EngineHandler
        self.engine_manager.bestmove_received.connect(self.engine_handler.handle_engine_best_move)
        
        # B. Repaint requests from overlay go directly to BoardController signals
        self.overlay_handler.request_repaint.connect(self.board_controller.state_changed)
        
        # C. When human selections change, query threat overlays
        self.board_controller.selection_changed.connect(self.overlay_handler.query_active_debug_overlay)
        
        # D. When a move is executed, decide who plays next
        self.board_controller.move_executed.connect(self._on_move_executed_coordination)
        
        # E. When a move is undone, sync overlays and legal moves list
        self.board_controller.move_undone.connect(self.overlay_handler.query_active_debug_overlay)
        self.board_controller.move_undone.connect(self.engine_handler.sync_position_and_query_legals)
        
        # F. Bind Engine played moves directly to board updates
        self.engine_handler.best_move_played.connect(self._on_engine_move_played)
        self.engine_handler.best_move_illegal.connect(self._on_engine_move_illegal)
        self.engine_handler.game_over_by_engine.connect(self.board_controller.game_over.emit)

    def _on_move_executed_coordination(self, san: str) -> None:
        """Decides threat queries and single-shot play schedules on move registrations."""
        self.overlay_handler.query_active_debug_overlay()
        self.engine_handler.sync_position_and_query_legals()
        
        # Trigger engine play loop if it's the engine's turn to play
        if self.engine_handler.is_engine_turn() and not self.board_state._board.is_game_over():
            QTimer.singleShot(150, self.engine_handler.trigger_engine_move)

    def _on_engine_move_played(self, move) -> None:
        """BoardController executes engine moves and handles selection updates."""
        if self.board_controller._execute_and_register_move(move) is not None:
            self.board_controller.highlight_manager.clear_selection()
            self.board_controller.state_changed.emit()

    def _on_engine_move_illegal(self, move_str: str) -> None:
        """Undoes human's last move if calculated engine move was illegal."""
        logger.error(f"Engine calculated an illegal move: {move_str}. Reverting last move...")
        self.board_controller.undo_last_move()

    # --- Backward-compatible delegating methods for MainWindow / UI connections ---
    
    @property
    def engine_mode(self) -> str:
        return self.engine_handler.engine_mode
        
    @engine_mode.setter
    def engine_mode(self, mode: str) -> None:
        self.engine_handler.engine_mode = mode

    def handle_square_clicked(self, square_idx: int | None) -> None:
        is_active = (self.engine_manager.engine_status == "Searching")
        is_turn = self.engine_handler.is_engine_turn()
        self.board_controller.handle_square_clicked(square_idx, is_active, is_turn)

    def undo_last_move(self) -> None:
        self.board_controller.undo_last_move()

    def set_debug_overlay_mode(self, mode: str) -> None:
        self.overlay_handler.set_debug_overlay_mode(mode)

    def query_active_debug_overlay(self) -> None:
        self.overlay_handler.query_active_debug_overlay()

    def trigger_engine_move(self) -> None:
        self.engine_handler.trigger_engine_move()

    def sync_position_and_query_legals(self) -> None:
        self.engine_handler.sync_position_and_query_legals()

    def cleanup(self) -> None:
        logger.info("Cleaning up GameController subprocesses...")
        self.engine_manager.quit_engine()
