from PySide6.QtCore import QObject, Signal
from enum import Enum, auto

class GameModes(Enum):
    PLAY_WHITE = auto()
    PLAY_BLACK = auto()
    ENGINE_VS_ENGINE = auto()
    HUMAN_VS_HUMAN = auto()

class GameState(QObject):
    game_mode_changed = Signal(GameModes)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._game_mode = GameModes.PLAY_WHITE
        self._result = None
        self._result_reason = None

    @property
    def mode(self) -> GameModes:
        return self._game_mode

    @mode.setter
    def game_mode(self, val: GameModes):
        if self._game_mode != val:
            self._game_mode = val
            self.game_mode_changed.emit(val)

    @property
    def result(self):
        return self._result
    
    @result.setter
    def result(self, val):
        self._result = val

    @property
    def result_reason(self):
        return self._result_reason
    
    @result_reason.setter
    def result_reason(self, val):
        self._result_reason = val

