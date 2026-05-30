# gui/controllers/handlers/engine_handler.py

from PySide6.QtCore import QObject, Signal
from gui.models.move import Move
from gui.core.app_state import app_state
from gui.utils.logger import get_logger

logger = get_logger(__name__)

class EngineHandler(QObject):
    # Signals emitted to request board changes or state signals from the orchestrator
    best_move_played = Signal(object)      # Emits Move object when engine calculated bestmove
    best_move_illegal = Signal(str)        # Emits move_str when calculated move was illegal
    game_over_by_engine = Signal(str)      # Emits outcome string when null move or engine-detected end

    def __init__(self, engine_manager, board_state, parent: QObject | None = None):
        super().__init__(parent)
        self.engine_manager = engine_manager
        self.board_state = board_state
        self.engine_mode = "play_black"  # Modes: "play_black", "play_white", "free_analysis", "two_human"

        # Wire status ready query
        self.engine_manager.status_changed.connect(self._handle_engine_status_for_legals)
        
        # Wire global engine settings overrides from AppState
        app_state.signals.engine_config_changed.connect(self._handle_engine_config_changed)

    def _handle_engine_status_for_legals(self, status: str) -> None:
        if status == "Ready":
            self.sync_position_and_query_legals()

    def sync_position_and_query_legals(self) -> None:
        """Sends current FEN to the engine and requests the up-to-date legal moves list."""
        if self.engine_manager.engine_status != "Disconnected":
            # Transmit active engine preferences loaded from preferences.json
            opts = app_state.engine_options
            self.engine_manager.send_command(f"setoption name Hash value {opts.get('Hash', 64)}")
            self.engine_manager.send_command(f"setoption name Threads value {opts.get('Threads', 1)}")
            
            fen = self.board_state.get_fen()
            self.engine_manager.send_position(fen)
            self.engine_manager.send_command("bluie-debug legalmoves")

    def is_engine_turn(self) -> bool:
        """Determines if it is currently the engine's turn to play based on active configuration."""
        if self.engine_mode == "play_black" and not self.board_state.turn:
            return True
        if self.engine_mode == "play_white" and self.board_state.turn:
            return True
        return False

    def trigger_engine_move(self) -> None:
        """Submits current FEN position and starts search to let engine play."""
        if not self.is_engine_turn():
            return
            
        logger.info("Triggering background engine search...")
        fen = self.board_state.get_fen()
        self.engine_manager.send_position(fen)
        self.engine_manager.start_search(depth=4)

    def handle_engine_best_move(self, move_str: str) -> None:
        """Slot responding to engine's calculation completion."""
        if not self.is_engine_turn():
            return
            
        logger.info(f"EngineHandler playing bestmove: {move_str}")

        # Check for engine null move (checkmate/stalemate game over indicators)
        if move_str == "0000" or self.board_state._board.is_game_over():
            board = self.board_state._board
            if board.is_checkmate():
                winner = "Black" if board.turn else "White"
                outcome = f"Checkmate! {winner} wins."
            elif board.is_stalemate():
                outcome = "Stalemate! The game is a draw."
            elif board.is_insufficient_material():
                outcome = "Draw due to insufficient material."
            elif board.is_fivefold_repetition() or board.is_threefold_repetition():
                outcome = "Draw due to repetition."
            else:
                outcome = "Game over."
            
            logger.info(f"Game Over detected by engine: {outcome}")
            self.game_over_by_engine.emit(outcome)
            return

        try:
            move = Move.from_uci(move_str)
            self.best_move_played.emit(move)
        except Exception as e:
            logger.error(f"Failed to decode bestmove '{move_str}': {e}", exc_info=True)
            self.best_move_illegal.emit(move_str)

    def _handle_engine_config_changed(self, options: dict) -> None:
        """Sends updated standard UCI options to the engine subprocess dynamically."""
        if self.engine_manager.engine_status != "Disconnected":
            if "Hash" in options:
                self.engine_manager.send_command(f"setoption name Hash value {options['Hash']}")
            if "Threads" in options:
                self.engine_manager.send_command(f"setoption name Threads value {options['Threads']}")
