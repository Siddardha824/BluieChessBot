from PySide6.QtCore import QObject, Signal

from ..models.board_state import BoardState
from ..services.move_helper import MoveHelper
from ..services.move_node import MoveNode
from gui.utils import get_logger

logger = get_logger(__name__)

class BoardManager(QObject):
    view_changed = Signal(object)

    def __init__(self, parent):
        super().__init__(parent)

        logger.info("Initializing board manager")
        self._state = BoardState(self)
        self._state.view_changed.connect(self.view_changed)

    def make_move(self, move: str) -> bool:
        success = MoveHelper.make_move(self._state, move)
        if success:
            logger.info("Move applied: %s", move)
        else:
            logger.warning("Move rejected: %s", move)
        return success
    
    def undo_move(self) -> str | None:
        return MoveHelper.undo_move(self._state)

    def new_game(self):
        logger.info("Starting new game")
        self._state.reset()

    def load_fen(self, fen: str):
        if self._state.is_valid_fen(fen):
            logger.info("Loading FEN: %s", fen)
            self._state.set_fen(fen)

    def get_fen(self) -> str:
        return self._state.fen

    def get_san_for_move(self, uci_move: str) -> str:
        return MoveHelper.get_san_for_move(self._state, uci_move)

    def format_uci_sequence(self, uci_moves: list[str]) -> str:
        return MoveHelper.format_uci_sequence(self._state, uci_moves)

    def get_export_state(self) -> MoveNode:
        return self._state.game_tree

