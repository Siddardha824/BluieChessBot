from PySide6.QtCore import QObject, Signal

from ..models.board_state import BoardState
from ..services.move_helper import MoveHelper
from gui.utils import get_logger

logger = get_logger(__name__)

class BoardManager(QObject):
    view_changed = Signal(object)

    def __init__(self, parent=None):
        super().__init__(parent)

        logger.info("Initializing board manager")
        self._board_state = BoardState(self)
        self._board_state.view_changed.connect(self.view_changed)

    def make_move(self, move: str) -> bool:
        success = MoveHelper.make_move(self._board_state, move)
        if success:
            logger.info("Move applied: %s", move)
        else:
            logger.warning("Move rejected: %s", move)
        return success
    
    def undo_move(self) -> str | None:
        return MoveHelper.undo_move(self._board_state)

    def new_game(self):
        logger.info("Starting new game")
        self._board_state.reset()

    def load_fen(self, fen: str):
        if self._board_state.is_valid_fen(fen):
            logger.info("Loading FEN: %s", fen)
            self._board_state.set_fen(fen)

    def get_san_for_move(self, uci_move: str) -> str:
        return MoveHelper.get_san_for_move(self._board_state, uci_move)

    def format_uci_sequence(self, uci_moves: list[str]) -> str:
        return MoveHelper.format_uci_sequence(self._board_state, uci_moves)

