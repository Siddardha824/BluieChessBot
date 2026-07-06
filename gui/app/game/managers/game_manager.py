from PySide6.QtCore import QObject, Signal, QTimer
import chess
from ..models.game_state import GameState, GameMode
from gui.utils import get_logger

logger = get_logger(__name__)

class GameManager(QObject):

    def __init__(self, parent=None):
        super().__init__(parent)
        self._state = GameState(self)

    @property
    def mode(self):
        """Gets the Current Game Mode"""
        return self._state.mode
    
    @mode.setter
    def mode(self, val: GameMode):
        self._state.mode = val

    def start_game(self):
        pass

    def stop_game(self):
        pass

    def _on_view_changed(self):
        pass

    def _on_position_changed(self, fen: str):
        pass

    def _trigger_next_action(self):
        pass

    def _on_loop_timeout(self):
        pass

    def _start_engine_search(self):
        pass

    def _on_best_move_updated(self, best_move: str):
        pass

