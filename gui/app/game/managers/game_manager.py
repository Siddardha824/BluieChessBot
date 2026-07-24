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

    # Game Event Signals
    game_started = Signal()
    game_stopped = Signal()
    game_saved = Signal()
    game_over = Signal(str, str) # result, reason

    # Game Service Signals
    setup_engine = Signal(str, str) # Engine name, Engine path
    remove_engine = Signal(str) # Engine name
    set_engine_position = Signal(str, str) # Engine name, Position FEN string
    start_engine_search = Signal(str) # Engine name
    stop_engine_search = Signal(str) # Engine name
    new_game = Signal()
    make_move = Signal(str) # UCI move string

    def __init__(self, parent):
        super().__init__(parent)
        self._state = GameState(self)

        self._game_service = GameService(self, self._state)
        self._connect_signals()

        self._state.match_status_changed.connect(self._on_match_status_changed)

        logger.info("Game Manager Initialized")


    @property
    def mode(self) -> GameMode:
        return self._state.mode
    
    @mode.setter
    def mode(self, val: GameMode):
        self._state.mode = val

    @property
    def status(self) -> MatchStatus:
        return self._state.match_status

    def start_game(self, white_path: str = "", black_path: str = ""):
        self._game_service.start_game(white_path, black_path)
        self.game_started.emit()

    def stop_game(self):
        self._game_service.abort_game()
        self.game_stopped.emit()

    def get_active_engines(self) -> list | None:
        match (self.mode):
            case GameMode.ANALYSIS: return None
            case GameMode.PLAY_WHITE: return [self._game_service._white_engine]
            case GameMode.PLAY_BLACK: return [self._game_service._black_engine]
            case GameMode.ENGINE_VS_ENGINE: return [self._game_service._white_engine, self._game_service._black_engine]

    def save_game(self, filepath: str, root_node: MoveNode, engine_info: dict):
        success = GameSaver.save_pgn(filepath, root_node, engine_info)
        if success:
            self.game_saved.emit()

    def on_view_changed(self, node: MoveNode | ChildMoveNode):
        self._game_service.on_view_changed(node)

    def on_best_move_updated(self, engine_name: str, best_move: str):
        self._game_service.on_best_move_updated(engine_name, best_move)


    def _on_match_status_changed(self, status: MatchStatus):
        """Translates backend status changes into UI-friendly signals."""
        if status == MatchStatus.CHECKMATE:
            result = "1-0" if self._state.current_turn == chess.BLACK else "0-1"
            self.game_over.emit(result, "Checkmate")
        elif status == MatchStatus.DRAW:
            self.game_over.emit("1/2-1/2", "Draw")
        elif status == MatchStatus.ABORTED:
            self.game_stopped.emit()

    def _connect_signals(self):
        self._game_service.setup_engine.connect(self.setup_engine.emit)
        self._game_service.remove_engine.connect(self.remove_engine.emit)
        self._game_service.set_engine_position.connect(self.set_engine_position.emit)
        self._game_service.start_engine_search.connect(self.start_engine_search.emit)
        self._game_service.stop_engine_search.connect(self.stop_engine_search.emit)
        self._game_service.new_game.connect(self.new_game.emit)
        self._game_service.make_move.connect(self.make_move.emit)
