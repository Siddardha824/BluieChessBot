from PySide6.QtCore import QObject, Signal
from enum import Enum, auto
from gui.utils import get_logger

logger = get_logger(__name__)

class GameModes(Enum):
    PLAY_WHITE = auto()
    PLAY_BLACK = auto()
    ENGINE_VS_ENGINE = auto()
    ANALYSIS = auto()

class GameState(QObject):
    game_mode_changed = Signal(GameModes)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._game_mode = GameModes.ANALYSIS  # Default to Analysis mode
        self._result = None
        self._result_reason = None

    @property
    def mode(self) -> GameModes:
        return self._game_mode

    @mode.setter
    def mode(self, val: GameModes):
        if self._game_mode != val:
            logger.info("Game mode changed: %s -> %s", self._game_mode.name, val.name)
            self._game_mode = val
            self.game_mode_changed.emit(val)

    @property
    def result(self):
        return self._result
    
    @result.setter
    def result(self, val):
        logger.info("Game result set: %s", val)
        self._result = val

    @property
    def result_reason(self):
        return self._result_reason
    
    @result_reason.setter
    def result_reason(self, val):
        logger.info("Game result reason set: %s", val)
        self._result_reason = val
