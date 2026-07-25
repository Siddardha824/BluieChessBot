"""Game session manager facade.

This module provides the GameManager class, which coordinates game configurations,
saving/loading, event forwarding, and status updates between the UI/ViewModel and
the underlying GameService.
"""

from __future__ import annotations
from PySide6.QtCore import QObject, Signal
from ..models.game_state import GameState, GameMode, MatchStatus
from ..services.game_service import GameService
from ..services.game_saver import GameSaver
import chess
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from gui.app.board.services.move_node import MoveNode, ChildMoveNode

from gui.utils import get_logger

logger = get_logger(__name__)


class GameManager(QObject):
    """Provide a facade for controlling chess game session configurations and lifecycles.

    This manager orchestrates starting/stopping matches, serializing game histories,
    responding to board view changes, and routing command and event signals.

    Signals:
        game_started: Emitted when a new game session begins.
        game_stopped: Emitted when the game session is aborted or stopped.
        game_saved: Emitted when the game is successfully written to PGN format.
        game_over: Emitted when the match finishes (result_string, reason_string).
        setup_engine: Forwarded signal to initialize an engine subprocess.
        remove_engine: Forwarded signal to delete an engine subprocess.
        set_engine_position: Forwarded signal to configure an engine position.
        start_engine_search: Forwarded signal to trigger an engine search.
        stop_engine_search: Forwarded signal to halt an engine search.
        new_game: Forwarded signal to reset board elements.
        make_move: Forwarded signal to perform a move on the board.
    """

    # Game Event Signals
    game_started = Signal()
    game_stopped = Signal()
    game_saved = Signal()
    game_over = Signal(str, str)            # result, reason

    # Game Service Signals
    setup_engine = Signal(str, str)        # Engine name, Engine path
    remove_engine = Signal(str)            # Engine name
    set_engine_position = Signal(str, str) # Engine name, Position FEN string
    start_engine_search = Signal(str)      # Engine name
    stop_engine_search = Signal(str)       # Engine name
    new_game = Signal()
    make_move = Signal(str)                # UCI move string

    def __init__(self, parent):
        """Initialize the game manager.

        Args:
            parent: Qt parent object for memory management.
        """
        super().__init__(parent)
        self._state = GameState(self)

        self._game_service = GameService(self, self._state)
        self._connect_signals()

        self._state.match_status_changed.connect(self._on_match_status_changed)

        logger.info("Game Manager Initialized")

    @property
    def mode(self) -> GameMode:
        """Return the current game mode."""
        return self._state.mode

    @mode.setter
    def mode(self, val: GameMode):
        """Set the current game mode.

        Args:
            val: The new GameMode value.
        """
        self._state.mode = val

    @property
    def status(self) -> MatchStatus:
        """Return the current match status."""
        return self._state.match_status

    def start_game(self, white_path: str = "", black_path: str = ""):
        """Start a new game session.

        Args:
            white_path: Path to white player's engine executable (if applicable).
            black_path: Path to black player's engine executable (if applicable).
        """
        self._game_service.start_game(white_path, black_path)
        self.game_started.emit()

    def stop_game(self):
        """Stop/abort the active game session."""
        self._game_service.abort_game()
        self.game_stopped.emit()

    def get_active_engines(self) -> list | None:
        """Return a list of currently active engine profiles, or None if in analysis.

        Returns:
            A list containing the names/ids of active engines, or None.
        """
        match (self.mode):
            case GameMode.ANALYSIS:
                return None
            case GameMode.PLAY_WHITE:
                return [self._game_service._white_engine]
            case GameMode.PLAY_BLACK:
                return [self._game_service._black_engine]
            case GameMode.ENGINE_VS_ENGINE:
                return [self._game_service._white_engine, self._game_service._black_engine]

    def save_game(self, filepath: str, root_node: MoveNode, engine_info: dict):
        """Serialize and export the active game history to a file.

        Args:
            filepath: The target system path to write the PGN file.
            root_node: The root move node of the game tree.
            engine_info: A dictionary of active engine profiles to append to PGN headers.
        """
        success = GameSaver.save_pgn(filepath, root_node, engine_info)
        if success:
            self.game_saved.emit()

    def on_view_changed(self, node: MoveNode | ChildMoveNode):
        """Forward board view changes to the game service.

        Args:
            node: The new active move node in the game tree.
        """
        self._game_service.on_view_changed(node)

    def on_best_move_updated(self, engine_name: str, best_move: str):
        """Forward calculated engine moves to the game service.

        Args:
            engine_name: The identifier of the reporting engine.
            best_move: The best move found, in UCI notation.
        """
        self._game_service.on_best_move_updated(engine_name, best_move)

    def _on_match_status_changed(self, status: MatchStatus):
        """Translate backend match status changes into UI-friendly signals.

        Args:
            status: The new MatchStatus.
        """
        if status == MatchStatus.CHECKMATE:
            result = "1-0" if self._state.current_turn == chess.BLACK else "0-1"
            self.game_over.emit(result, "Checkmate")
        elif status == MatchStatus.DRAW:
            self.game_over.emit("1/2-1/2", "Draw")
        elif status == MatchStatus.ABORTED:
            self.game_stopped.emit()

    def _connect_signals(self):
        """Wire signals from the game service to the manager's public signals."""
        self._game_service.setup_engine.connect(self.setup_engine.emit)
        self._game_service.remove_engine.connect(self.remove_engine.emit)
        self._game_service.set_engine_position.connect(self.set_engine_position.emit)
        self._game_service.start_engine_search.connect(self.start_engine_search.emit)
        self._game_service.stop_engine_search.connect(self.stop_engine_search.emit)
        self._game_service.new_game.connect(self.new_game.emit)
        self._game_service.make_move.connect(self.make_move.emit)
