"""Board manager.

This module provides `BoardManager`, a thin QObject wrapper used by the
UI layer to interact with the underlying `BoardState` model and helper
services. `BoardManager` exposes a `view_changed` signal and convenience
methods that delegate work to `MoveHelper` and `BoardState`.
"""

from PySide6.QtCore import QObject, Signal

from ..models.board_state import BoardState
from ..services.move_helper import MoveHelper
from ..services.move_node import MoveNode
from gui.utils import get_logger

logger = get_logger(__name__)


class BoardManager(QObject):
    """Manage board interactions for the UI.

    `BoardManager` is a lightweight controller that holds a `BoardState`
    instance and exposes methods the UI can call (apply/undo moves,
    load FEN, query SAN/UCIs, etc.). It forwards most operations to
    `MoveHelper` or `BoardState` and emits `view_changed` when the
    underlying view is updated.

    Signals:
        view_changed(object): Emitted when the board view or selected node
            changes. The payload is the new view object (usually a node).
    """

    view_changed = Signal(object)

    def __init__(self, parent):
        """Create a new `BoardManager`.

        Args:
            parent: QObject parent for ownership in the Qt hierarchy.
        """
        super().__init__(parent)

        logger.info("Initializing board manager")
        self._state = BoardState(self)
        self._state.view_changed.connect(self.view_changed)

    def make_move(self, move: str) -> bool:
        """Apply a move to the current board state.

        This delegates to `MoveHelper.make_move` which handles move parsing
        and validation.

        Args:
            move: Move string (typically UCI) to apply.

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
            The UCI string for the undone move, or `None` if there was
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
            fen: FEN string to load.
        """
        if self._state.is_valid_fen(fen):
            logger.info("Loading FEN: %s", fen)
            self._state.set_fen(fen)

    def get_fen(self) -> str:
        """Return the current board position as a FEN string."""
        return self._state.fen

    def get_san_for_move(self, uci_move: str) -> str:
        """Return the SAN (algebraic) representation for a UCI move.

        Args:
            uci_move: Move in UCI notation.

        Returns:
            The SAN string for the move as formatted by `MoveHelper`.
        """
        return MoveHelper.get_san_for_move(self._state, uci_move)

    def format_uci_sequence(self, uci_moves: list[str]) -> str:
        """Format a sequence of UCI moves into a human-readable string.

        Args:
            uci_moves: List of moves in UCI notation.

        Returns:
            A formatted string (moves separated by spaces or move numbers)
            produced by `MoveHelper.format_uci_sequence`.
        """
        return MoveHelper.format_uci_sequence(self._state, uci_moves)

    def get_export_state(self) -> MoveNode:
        """Return the root `MoveNode` representing the current game tree.

        The returned object can be used for exporting the game or
        traversing variations.
        """
        return self._state.game_tree

