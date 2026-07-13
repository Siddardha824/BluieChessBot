from PySide6.QtCore import QObject, Signal
from enum import Enum, auto
import chess
from gui.utils import get_logger

logger = get_logger(__name__)

class GameMode(Enum):
    PLAY_WHITE = auto()
    PLAY_BLACK = auto()
    ENGINE_VS_ENGINE = auto()
    ANALYSIS = auto()

class MatchStatus(Enum):
    ACTIVE = auto()
    DRAW = auto()
    CHECKMATE = auto()
    STALEMATE = auto()
    RESIGNED = auto()
    ABORTED = auto()

class GameState(QObject):
    # Signals for UI/ViewModel reactivity
    game_mode_changed = Signal(GameMode)
    match_status_changed = Signal(MatchStatus)
    turn_changed = Signal(bool) # chess.WHITE (True) or chess.BLACK (False)
    clocks_updated = Signal(float, float) # white_time, black_time

    def __init__(self, parent):
        super().__init__(parent)
        self._game_mode = GameMode.ANALYSIS
        self._match_status = MatchStatus.ACTIVE
        self._current_turn = chess.WHITE
        self._white_time = 0.0
        self._black_time = 0.0

        self.game_mode_changed.emit(self._game_mode)

    @property
    def mode(self) -> GameMode:
        return self._game_mode

    @mode.setter
    def mode(self, val: GameMode):
        if self._game_mode != val:
            logger.info("Game mode changed: %s -> %s", self._game_mode.name, val.name)
            self._game_mode = val
            self.game_mode_changed.emit(val)

    @property
    def match_status(self) -> MatchStatus:
        return self._match_status
    
    @match_status.setter
    def match_status(self, val: MatchStatus):
        if self._match_status != val:
            logger.info("Match status changed: %s -> %s", self._match_status.name, val.name)
            self._match_status = val
            self.match_status_changed.emit(val)

    @property
    def current_turn(self) -> chess.Color:
        """Returns chess.WHITE (True) or chess.BLACK (False)"""
        return self._current_turn
    
    @current_turn.setter
    def current_turn(self, val: chess.Color):
        if self._current_turn != val:
            self._current_turn = val
            self.turn_changed.emit(val)

    def update_clocks(self, white_time: float, black_time: float):
        """Updates the clocks for both players and emits a signal."""
        self._white_time = white_time
        self._black_time = black_time
        self.clocks_updated.emit(white_time, black_time)

    def reset(self):
        """Resets the state properties for a fresh game."""
        self._match_status = MatchStatus.ACTIVE
        self._current_turn = chess.WHITE
        self.update_clocks(0.0, 0.0)

        # Emit signals to notify any observers of the reset state
        self.match_status_changed.emit(self._match_status)
        self.turn_changed.emit(self._current_turn)
        self.clocks_updated.emit(self._white_time, self._black_time)



