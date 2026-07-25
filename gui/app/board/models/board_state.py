"""Track the chess board state and PGN move tree.

This module provides the BoardState class, which wraps a cached PGN move tree
and active view node, emitting signals when the active node changes to trigger
reactive updates.
"""

from PySide6.QtCore import QObject, Signal
import chess
from ..services.move_node import MoveNode, ChildMoveNode
from typing import cast
from gui.utils import get_logger

logger = get_logger(__name__)


class BoardState(QObject):
    """Manage the active board view and the underlying game variation tree.

    This class maintains the root MoveNode and tracks the currently visible active
    node. It exposes accessors for board query operations (FEN, turn, legal moves)
    and mutation actions (make move, undo).

    Signals:
        view_changed: Emitted with the new view node when the active node changes.
    """

    view_changed = Signal(MoveNode)

    def __init__(self, parent):
        """Initialize the board state model.

        Args:
            parent: Qt parent object for QObject ownership.
        """
        super().__init__(parent)

        self._root_node = MoveNode()
        self._view_node = self._root_node

        self._sync_view(self._view_node)

    @property
    def board(self) -> chess.Board:
        """Return a copy of the current board for the active view node."""
        return self._view_node.board()

    @property
    def game_tree(self) -> MoveNode:
        """Return the root MoveNode representing the game tree."""
        return self._root_node

    @property
    def fen(self) -> str:
        """Return the FEN string for the current board view."""
        return self.board.fen()

    @property
    def turn(self) -> chess.Color:
        """Return the turn side for the current board (True for White)."""
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
        """Return a copy of the current board's move list."""
        return self.board.move_stack.copy()

    @property
    def legal_moves(self):
        """Return the legal moves generator for the current board position."""
        return self.board.legal_moves

    def is_legal(self, move: chess.Move) -> bool:
        """Determine if a move is legal in the current board position.

        Args:
            move: The chess.Move instance to evaluate.

        Returns:
            True if the move is legal, False otherwise.
        """
        return self.board.is_legal(move)

    def copy(self) -> chess.Board:
        """Return a copy of the current board object.

        This is useful for read-only inspection or move simulation without
        mutating the internal state.
        """
        return self.board

    def san(self, move: chess.Move) -> str:
        """Convert a move to its Standard Algebraic Notation (SAN) string.

        Args:
            move: The chess.Move instance to format.

        Returns:
            The SAN representation of the move.
        """
        return self.board.san(move)

    def set_fen(self, fen: str):
        """Replace the current game tree with a new root node set up from a FEN string.

        Args:
            fen: The FEN string representing the starting board.
        """
        self._root_node = MoveNode()
        self._root_node.setup(fen)
        self._view_node = self._root_node

        self._sync_view(self._view_node)

    def is_valid_fen(self, fen: str) -> bool:
        """Validate a FEN string.

        Args:
            fen: The FEN string to validate.

        Returns:
            True if the FEN represents a valid board, False otherwise.
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
        """Apply a move to the current view by creating and selecting a child node.

        Args:
            move: The chess.Move instance to apply.
        """
        new_node = self._view_node.add_variation(move)
        self._view_node = cast(ChildMoveNode, new_node)

        self._sync_view(self._view_node)

    def undo(self) -> chess.Move | None:
        """Undo the last applied move on the current view.

        Returns:
            The undone chess.Move instance.

        Raises:
            IndexError: If there are no moves to undo.
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
        """Emit the view_changed signal for the given node.

        Args:
            node: The new active move node.
        """
        self.view_changed.emit(node)
