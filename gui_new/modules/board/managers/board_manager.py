from PySide6.QtCore import QObject, Signal

from ..models.game_state import GameState
from ..models.board_state import BoardState
from ..services.move_executor import MoveExecutor

class BoardManager(QObject):
    position_changed = Signal(str)    

    def __init__(self, parent=None):
        super().__init__(parent)

        self._game_state = GameState(self)
        self._board_state = BoardState(self)
        self._board_state.position_changed.connect(
            self.position_changed.emit
        )

    @property
    def game_state(self) -> GameState:
        return self._game_state
    
    @property
    def board(self) -> BoardState:
        return self._board_state

    def make_move(self, move: str) -> bool:
        success = MoveExecutor.make_move(self._board_state, move)
        return success
    
    def undo_move(self) -> str | None:
        return MoveExecutor.undo_move(self._board_state)

    def new_game(self):
        self._board_state.reset()

    def load_fen(self, fen: str):
        self._board_state.set_fen(fen)

