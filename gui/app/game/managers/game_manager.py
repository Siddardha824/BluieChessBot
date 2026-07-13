from PySide6.QtCore import QObject, Signal
from ..models.game_state import GameState, GameMode, MatchStatus
from ..services.game_service import GameService
import chess
from gui.utils import get_logger

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from gui.app.app_manager import AppManager

logger = get_logger(__name__)

class GameManager(QObject):
    game_started = Signal()
    game_stopped = Signal()
    game_over = Signal(str, str) # result, reason


    def __init__(self, parent, app_manager: AppManager):
        super().__init__(parent)
        self._state = GameState(self)
        self._app = app_manager

        self._game_service = GameService(self, self._state, self._app)

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

    def _on_match_status_changed(self, status: MatchStatus):
        """Translates backend status changes into UI-friendly signals."""
        if status == MatchStatus.CHECKMATE:
            result = "1-0" if self._state.current_turn == chess.BLACK else "0-1"
            self.game_over.emit(result, "Checkmate")
        elif status == MatchStatus.DRAW:
            self.game_over.emit("1/2-1/2", "Draw")
        elif status == MatchStatus.ABORTED:
            self.game_stopped.emit()
