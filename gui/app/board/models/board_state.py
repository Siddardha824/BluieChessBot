"""Board state model that tracks a PGN tree and exposes a viewable board.

This module provides `BoardState`, a Qt `QObject` wrapper around a cached
PGN move tree (using `MoveNode`) and a current view node. It emits
`view_changed` when the active view node changes so UI components can
react to updates.
"""

from PySide6.QtCore import QObject, Signal
import chess
from ..services.move_node import MoveNode, ChildMoveNode
from typing import cast
from gui.utils import get_logger

logger = get_logger(__name__)


class BoardState(QObject):
    """Represents the current board view and underlying game tree.

    The `BoardState` keeps a root `MoveNode` representing the game and a
    reference to the currently visible node (`_view_node`). Consumers can
    query board properties (FEN, turn, legal moves, etc.) and apply or undo
    moves. The object emits the `view_changed` Qt signal when the view node
    changes.

    Signals:
        view_changed (MoveNode): emitted with the new view node whenever the
            active node changes.
    """

    view_changed = Signal(MoveNode)

    def __init__(self, parent):
        """Initialize an empty board state attached to a Qt parent.

        Args:
            parent: Qt parent object for QObject ownership.
        """
        super().__init__(parent)

        self._root_node = MoveNode()
        self._view_node = self._root_node

        self._sync_view(self._view_node)

    @property
    def board(self) -> chess.Board:
        """Return a copy of the current board for the active view node.

        This is a convenience accessor that delegates to the active node's
        cached board and returns a copy to avoid external mutation.
        """
        return self._view_node.board()

    @property
    def game_tree(self) -> MoveNode:
        """Return the root `MoveNode` representing the full game tree."""
        return self._root_node

    @property
    def fen(self) -> str:
        """Return the FEN string for the current board view."""
        return self.board.fen()

    @property
    def turn(self) -> chess.Color:
        """Return the side to move for the current board (True=white)."""
        return self.board.turn
    
    @property
    def is_start_pos(self) -> bool:
        """Return True if the current view is the root (start position)."""
        return self._root_node == self._view_node

    @property
    def fullmove_number(self) -> int:
        """Return the fullmove number from the current board view."""
        return self.board.fullmove_number

    @property
    def halfmove_clock(self) -> int:
        """Return the halfmove clock from the current board view."""
        return self.board.halfmove_clock
    
    @property
    def move_stack(self) -> list[chess.Move]:
        """Return a copy of the current board's move stack (list of `chess.Move`)."""
        return self.board.move_stack.copy()

    @property
    def legal_moves(self):
        """Return the `legal_moves` generator for the current board view."""
        return self.board.legal_moves
    
    def is_legal(self, move: chess.Move) -> bool:
        """Return True if `move` is legal in the current board view."""
        return self.board.is_legal(move)
    
    def copy(self) -> chess.Board:
        """Return a copy of the current board object.

        This method intentionally returns a board instance suitable for
        read-only inspection or for simulating moves without changing the
        internal view.
        """
        return self.board

    def san(self, move: chess.Move) -> str:
        """Return the SAN string for `move` using the current board context."""
        return self.board.san(move)

    def set_fen(self, fen: str):
        """Replace the current game with a new root node set up from `fen`.

        Args:
            fen: A FEN string representing the starting board.
        """
        self._root_node = MoveNode()
        self._root_node.setup(fen)
        self._view_node = self._root_node

        self._sync_view(self._view_node)

    def is_valid_fen(self, fen: str):
        """Validate a FEN string and return True if it represents a valid board.

        Logs a warning and returns False for invalid FEN strings.
        """
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
        """Reset the game to a new root (standard start position)."""
        self._root_node = MoveNode()
        self._view_node = self._root_node

        self._sync_view(self._view_node)

    def move(self, move: chess.Move):
        """Apply `move` to the current view by creating and switching to a child node.

        Args:
            move: A `chess.Move` instance to apply.
        """
        new_node = self._view_node.add_variation(move)
        self._view_node = cast(ChildMoveNode, new_node)

        self._sync_view(self._view_node)

    def undo(self) -> chess.Move | None:
        """Undo the last applied move on the current view.

        Returns the undone `chess.Move` or raises `IndexError` if there are no
        moves to undo.
        """
        if self._view_node is self._root_node or self._view_node.parent is None:
            raise IndexError("No moves to undo")

        moved = self._view_node.move
        self._view_node = cast(MoveNode | ChildMoveNode, self._view_node.parent)
        self._sync_view(self._view_node)
        return moved

    def can_undo(self) -> bool:
        """Return True if there is at least one move to undo from the current view."""
        return self._view_node is not self._root_node and self._view_node.parent is not None

    def _sync_view(self, node: MoveNode | ChildMoveNode):
        """Emit the `view_changed` signal for `node`.

        This internal helper centralizes emitting the Qt signal whenever the
        view node changes.
        """
        self.view_changed.emit(node)

