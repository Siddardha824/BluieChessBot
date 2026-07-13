from PySide6.QtCore import QObject, Signal
import chess
from ..services.move_node import MoveNode, ChildMoveNode
from typing import cast
from gui.utils import get_logger

logger = get_logger(__name__)


class BoardState(QObject):
    view_changed = Signal(MoveNode)

    def __init__(self, parent):
        super().__init__(parent)

        self._root_node = MoveNode()
        self._view_node = self._root_node

        self._sync_view(self._view_node)

    @property
    def board(self) -> chess.Board:
        return self._view_node.board()

    @property
    def game_tree(self) -> MoveNode:
        return self._root_node

    @property
    def fen(self) -> str:
        return self.board.fen()

    @property
    def turn(self) -> chess.Color:
        return self.board.turn
    
    @property
    def is_start_pos(self) -> bool:
        return self._root_node == self._view_node

    @property
    def fullmove_number(self) -> int:
        return self.board.fullmove_number

    @property
    def halfmove_clock(self) -> int:
        return self.board.halfmove_clock
    
    @property
    def move_stack(self) -> list[chess.Move]:
        return self.board.move_stack.copy()

    @property
    def legal_moves(self):
        return self.board.legal_moves
    
    def is_legal(self, move: chess.Move) -> bool:
        return self.board.is_legal(move)
    
    def copy(self) -> chess.Board:
        return self.board

    def san(self, move: chess.Move) -> str:
        return self.board.san(move)

    def set_fen(self, fen: str):
        self._root_node = MoveNode()
        self._root_node.setup(fen)
        self._view_node = self._root_node

        self._sync_view(self._view_node)

    def is_valid_fen(self, fen: str):
        try:
            board = chess.Board(fen)

            if board.is_valid():
                return True
            else:
                logger.warning("Given FEN " + fen + " is invalid")
                return False
        except ValueError:
            logger.warning("Given FEN " + fen + " is invalid")
            return False

    def reset(self):
        self._root_node = MoveNode()
        self._view_node = self._root_node

        self._sync_view(self._view_node)

    def move(self, move: chess.Move):
        new_node = self._view_node.add_variation(move)
        self._view_node = cast(ChildMoveNode, new_node)

        self._sync_view(self._view_node)

    def undo(self) -> chess.Move | None:
        if self._view_node is self._root_node or self._view_node.parent is None:
            raise IndexError("No moves to undo")

        moved = self._view_node.move
        self._view_node = cast(MoveNode | ChildMoveNode, self._view_node.parent)
        self._sync_view(self._view_node)
        return moved

    def can_undo(self) -> bool:
        return self._view_node is not self._root_node and self._view_node.parent is not None

    def _sync_view(self, node: MoveNode | ChildMoveNode):
        self.view_changed.emit(node)

    

