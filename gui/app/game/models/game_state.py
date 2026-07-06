from PySide6.QtCore import QObject, Signal
from enum import Enum, auto
from gui.utils import get_logger

logger = get_logger(__name__)

class GameMode(Enum):
    PLAY_WHITE = auto()
    PLAY_BLACK = auto()
    ENGINE_VS_ENGINE = auto()
    ANALYSIS = auto()

class GameState(QObject):
    game_mode_changed = Signal(GameMode)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._game_mode = GameMode.ANALYSIS

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

