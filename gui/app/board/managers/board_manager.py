from PySide6.QtCore import QObject, Signal

from ..models.game_state import GameState
from ..models.board_state import BoardState
from ..services.move_executor import MoveExecutor
from gui.utils import get_logger


logger = get_logger(__name__)

class BoardManager(QObject):
    position_changed = Signal(str)    

    def __init__(self, parent=None):
        super().__init__(parent)

        logger.info("Initializing board manager")
        self._game_state = GameState(self)
        self._board_state = BoardState(self)
        self._board_state.position_changed.connect(
            self.position_changed.emit
        )

    @property
    def game_state(self) -> GameState:
        return self._game_state
    
    @property
    def getSession(self) -> BoardState:
        return self._board_state

    def make_move(self, move: str) -> bool:
        success = MoveExecutor.make_move(self._board_state, move)
        if success:
            logger.info("Move applied: %s", move)
        else:
            logger.warning("Move rejected: %s", move)
        return success
    
    def undo_move(self) -> str | None:
        return MoveExecutor.undo_move(self._board_state)

    def new_game(self):
        logger.info("Starting new game")
        self._board_state.reset()

    def load_fen(self, fen: str):
        logger.info("Loading FEN: %s", fen)
        self._board_state.set_fen(fen)

