"""Game session control and coordination service.

This module provides the GameService class, which manages the active game loop,
coordinating turns, moves, engine search triggers, and game states based on the
active GameMode.
"""

from __future__ import annotations
from PySide6.QtCore import QObject, Signal
import chess
from ..models.game_state import GameState, GameMode, MatchStatus

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from gui.app.board.services.move_node import MoveNode, ChildMoveNode

from gui.utils import get_logger
logger = get_logger(__name__)


class GameService(QObject):
    """Manage the active game play session and coordinate chess engine actions.

    This service connects user actions, board updates, and engine analysis searches,
    handling the transitioning of state, initialization of engines for specific
    game modes, and processing of best move results.

    Signals:
        setup_engine: Emitted to initialize an engine subprocess (engine_name, path).
        remove_engine: Emitted to terminate an engine subprocess (engine_name).
        set_engine_position: Emitted to update an engine's internal board FEN (engine_name, FEN).
        start_engine_search: Emitted to tell an engine to begin searching (engine_name).
        stop_engine_search: Emitted to tell an engine to halt search (engine_name).
        new_game: Emitted to reset board elements for a new game.
        make_move: Emitted to apply a move on the board (uci_move_string).
    """

    # Engine control signals
    setup_engine = Signal(str, str)        # Engine name, Engine path
    remove_engine = Signal(str)            # Engine name
    set_engine_position = Signal(str, str) # Engine name, Position FEN string
    start_engine_search = Signal(str)      # Engine name
    stop_engine_search = Signal(str)       # Engine name

    # Board control signals
    new_game = Signal()
    make_move = Signal(str)                # UCI move string

    def __init__(self, parent, state: GameState):
        """Initialize the game service.

        Args:
            parent: Qt parent object for memory management.
            state: GameState model representing active game configuration and status.
        """
        super().__init__(parent)

        self._state = state

        self._white_engine: str | None = None
        self._black_engine: str | None = None

        self._current_fen: str = chess.STARTING_FEN

        logger.info("Game Service Initialized")

    def _setup_engine(self, engine_name: str, engine_path: str):
        """Request setup of an engine subprocess.

        Args:
            engine_name: The name/id of the engine to initialize.
            engine_path: System executable path of the engine.
        """
        if not engine_path:
            logger.error(f"Cannot setup an engine {engine_name}: No path provided")
            return

        self.setup_engine.emit(engine_name, engine_path)

    def _cleanup_engines(self):
        """Clean up active white and black engines by emitting removal signals."""
        if self._white_engine:
            self.remove_engine.emit(self._white_engine)
        if self._black_engine:
            self.remove_engine.emit(self._black_engine)

        self._white_engine = None
        self._black_engine = None

    def start_game(self, white_path: str = "", black_path: str = ""):
        """Start a new game session with configurations matching the game mode.

        Args:
            white_path: Path to white player's engine executable (if applicable).
            black_path: Path to black player's engine executable (if applicable).
        """
        logger.info(f"Game Service starting a game in Mode: {self._state.mode}")

        self._cleanup_engines()

        match self._state.mode:
            case GameMode.ANALYSIS:
                self._start_analysis(white_path)
            case GameMode.PLAY_WHITE:
                self._start_game_white(black_path)
            case GameMode.PLAY_BLACK:
                self._start_game_black(white_path)
            case GameMode.ENGINE_VS_ENGINE:
                self._start_game_engine(white_path, black_path)

        self.new_game.emit()
        self._state.reset()

        self._trigger_next_action()

    def end_game(self):
        """Stop any active engine searches to end the game session."""
        if self._white_engine:
            self.stop_engine_search.emit(self._white_engine)
        if self._black_engine:
            self.stop_engine_search.emit(self._black_engine)

    def abort_game(self):
        """Abort the active game session and stop all engine searches."""
        if self._white_engine:
            self.stop_engine_search.emit(self._white_engine)
        if self._black_engine:
            self.stop_engine_search.emit(self._black_engine)

        self._state.match_status = MatchStatus.ABORTED

    def _start_analysis(self, engine_path: str):
        """Configure and start the session in analysis mode.

        Args:
            engine_path: System executable path of the engine.
        """
        self._white_engine = "Analysis"
        self._setup_engine(self._white_engine, engine_path)

    def _start_game_white(self, black_engine_path: str):
        """Configure the session for a human playing White against a Black engine.

        Args:
            black_engine_path: System executable path of the Black engine.
        """
        self._black_engine = "Black"
        self._setup_engine(self._black_engine, black_engine_path)

    def _start_game_black(self, white_engine_path: str):
        """Configure the session for a human playing Black against a White engine.

        Args:
            white_engine_path: System executable path of the White engine.
        """
        self._white_engine = "White"
        self._setup_engine(self._white_engine, white_engine_path)

    def _start_game_engine(self, white_engine_path: str, black_engine_path: str):
        """Configure the session for an engine vs. engine match.

        Args:
            white_engine_path: System executable path of the White engine.
            black_engine_path: System executable path of the Black engine.
        """
        self._white_engine = "White"
        self._black_engine = "Black"
        self._setup_engine(self._white_engine, white_engine_path)
        self._setup_engine(self._black_engine, black_engine_path)

    def on_view_changed(self, node: MoveNode | ChildMoveNode):
        """Process changes in the board view and evaluate game termination rules.

        Args:
            node: The new active move node in the game tree.
        """
        board = node.board()
        self._state.current_turn = board.turn
        self._current_fen = board.fen()

        if board.is_checkmate():
            self._state.match_status = MatchStatus.CHECKMATE
            self.end_game()

        if board.is_game_over(claim_draw=True):
            self._state.match_status = MatchStatus.DRAW
            self.end_game()
            return

        if self._state.match_status == MatchStatus.ACTIVE:
            self._trigger_next_action()

    def on_best_move_updated(self, engine_name: str, best_move: str):
        """Process best moves calculated by engines and play them if matching turn.

        Args:
            engine_name: The identifier of the reporting engine.
            best_move: The best move found, in UCI notation.
        """
        expected_engine = self._get_active_engine_for_turn()

        if expected_engine and engine_name == expected_engine:
            if self._state.mode in [GameMode.PLAY_WHITE, GameMode.PLAY_BLACK, GameMode.ENGINE_VS_ENGINE]:
                logger.info("%s played: %s", engine_name, best_move)
                self.make_move.emit(best_move)

    def _trigger_next_action(self):
        """Determine and trigger the next action (e.g. starting a search) for the turn."""
        if self._state.match_status != MatchStatus.ACTIVE:
            return

        active_engine = self._get_active_engine_for_turn()

        if self._state.mode == GameMode.ANALYSIS and self._white_engine:
            self._start_engine_search(self._white_engine)
        elif active_engine:
            self._start_engine_search(active_engine)

    def _get_active_engine_for_turn(self) -> str | None:
        """Return the name of the active engine whose turn it is.

        Returns:
            The engine identifier string, or None if the current player is human.
        """
        if self._state.current_turn == chess.WHITE:
            return self._white_engine
        else:
            return self._black_engine

    def _start_engine_search(self, engine_name: str):
        """Instruct the specified engine to begin search analysis.

        Args:
            engine_name: The identifier of the target engine.
        """
        logger.info("Triggering %s search for FEN: %s", engine_name, self._current_fen)

        self.set_engine_position.emit(engine_name, self._current_fen)
        self.start_engine_search.emit(engine_name)
