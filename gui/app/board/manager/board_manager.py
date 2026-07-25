"""Provide the BoardManager facade controller.

This module provides the BoardManager class, which acts as a lightweight QObject
wrapper for UI layer components to interact with the underlying BoardState model
and helper services.
"""

from PySide6.QtCore import QObject, Signal

from ..models.board_state import BoardState
from ..services.move_helper import MoveHelper
from ..services.move_node import MoveNode
from gui.utils import get_logger

logger = get_logger(__name__)


class BoardManager(QObject):
    """Manage chess board interactions and delegate requests to board services.

    This controller acts as a facade holding a BoardState instance and exposing
    methods to apply or undo moves, load FEN positions, format SAN sequences, and
    query the game tree.

    Signals:
        view_changed: Emitted when the board view or selected node changes.
    """

    view_changed = Signal(object)

    def __init__(self, parent):
        """Initialize the board manager.

        Args:
            parent: QObject parent for ownership in the Qt hierarchy.
        """
        super().__init__(parent)

        logger.info("Initializing board manager")
        self._state = BoardState(self)
        self._state.view_changed.connect(self.view_changed)

    def make_move(self, move: str) -> bool:
        """Apply a move to the current board state.

        Args:
            move: The move string (typically UCI) to apply.

        Returns:
            True if the move was successfully applied, False otherwise.
        """
        success = MoveHelper.make_move(self._state, move)
        if success:
            logger.info("Move applied: %s", move)
        else:
            logger.warning("Move rejected: %s", move)
        return success

    def undo_move(self) -> str | None:
        """Undo the last move on the current board.

        Returns:
            The UCI string for the undone move, or None if there was
            no move to undo.
        """
        return MoveHelper.undo_move(self._state)

    def new_game(self):
        """Reset the board state to the starting position."""
        logger.info("Starting new game")
        self._state.reset()

    def load_fen(self, fen: str):
        """Load a FEN string into the board state if it is valid.

        Args:
            fen: The FEN string to load.
        """
        if self._state.is_valid_fen(fen):
            logger.info("Loading FEN: %s", fen)
            self._state.set_fen(fen)

    def get_fen(self) -> str:
        """Return the current board position as a FEN string."""
        return self._state.fen

    def get_san_for_move(self, uci_move: str) -> str:
        """Return the Standard Algebraic Notation (SAN) representation for a UCI move.

        Args:
            uci_move: The move in UCI notation.

        Returns:
            The SAN string for the move.
        """
        return MoveHelper.get_san_for_move(self._state, uci_move)

    def format_uci_sequence(self, uci_moves: list[str]) -> str:
        """Format a sequence of UCI moves into a human-readable string.

        Args:
            uci_moves: A list of moves in UCI notation.

        Returns:
            A space-separated SAN sequence of moves.
        """
        return MoveHelper.format_uci_sequence(self._state, uci_moves)

    def get_export_state(self) -> MoveNode:
        """Return the root MoveNode representing the game tree.

        Returns:
            The root MoveNode of the active chess game.
        """
        return self._state.game_tree
