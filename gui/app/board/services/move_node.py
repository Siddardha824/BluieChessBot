"""Manage PGN move nodes with cached board states for efficient board reconstruction.

This module provides the MoveNode and ChildMoveNode classes, which wrap standard
python-chess PGN node structures and cache board states to prevent repeated, expensive
replays when traversing variation trees.
"""

from chess.pgn import Game, ChildNode
from chess import Move, Board
from typing import Iterable, Union, List


class MoveNode(Game):
    """Represent a root PGN game tree node with a cached board state.

    This node overrides board cache operations and provides convenient property accessors
    for retrieving/updating PGN headers such as players, outcomes, and results.
    """

    variations: List["ChildMoveNode"]  # pyright: ignore[reportIncompatibleVariableOverride]

    def __init__(self, *args, **kwargs):
        """Initialize the root move node and cache its starting board state."""
        super().__init__(*args, **kwargs)
        self._cached_board = super().board()

    def setup(self, board: Union[Board, str]) -> None:
        """Set up the game tree from a board or FEN string and cache the board state.

        Args:
            board: A chess.Board instance or FEN string to initialize from.
        """
        super().setup(board)
        self._cached_board = super().board()

    def board(self) -> Board:
        """Return a copy of the cached board state for this game node."""
        return self._cached_board.copy()

    @property
    def result(self) -> str:
        """Return the game result header value (e.g. '1-0', '1/2-1/2')."""
        return self.headers.get("Result", "*")

    @result.setter
    def result(self, value: str) -> None:
        """Set the game result header.

        Args:
            value: The result string.
        """
        self.headers["Result"] = value

    @property
    def result_reason(self) -> str:
        """Return the game termination reason header."""
        return self.headers.get("Termination", "")

    @result_reason.setter
    def result_reason(self, reason: str) -> None:
        """Set the game termination reason header.

        Args:
            reason: The termination reason text.
        """
        self.headers["Termination"] = reason

    def set_outcome(self, result: str, reason: str) -> None:
        """Set both the game result and the termination reason in one call.

        Args:
            result: The result header value.
            reason: The termination reason header value.
        """
        self.result = result
        self.result_reason = reason

    @property
    def white(self) -> str:
        """Return the name of the White player."""
        return self.headers["White"]

    @white.setter
    def white(self, white_player: str) -> None:
        """Set the name of the White player.

        Args:
            white_player: The name of the player.
        """
        self.headers["White"] = white_player

    @property
    def black(self) -> str:
        """Return the name of the Black player."""
        return self.headers["Black"]

    @black.setter
    def black(self, black_player: str) -> None:
        """Set the name of the Black player.

        Args:
            black_player: The name of the player.
        """
        self.headers["Black"] = black_player

    def add_variation(
        self,
        move: Move,
        *,
        comment: str = "",
        starting_comment: str = "",
        nags: Iterable[int] = (),
    ) -> "ChildMoveNode":
        """Add a variation move node as the next variation.

        Args:
            move: The chess.Move to add.
            comment: Optional comment to attach to the move.
            starting_comment: Optional starting comment to attach.
            nags: Optional iterable of Numeric Annotation Glyphs (NAGs).

        Returns:
            The created ChildMoveNode.
        """
        child = ChildMoveNode(
            self,
            move,
            comment=comment,
            starting_comment=starting_comment,
            nags=nags,
        )
        return child

    def add_main_variation(
        self,
        move: Move,
        *,
        comment: str = "",
        starting_comment: str = "",
        nags: Iterable[int] = (),
    ) -> "ChildMoveNode":
        """Insert a variation move node as the main variation.

        Args:
            move: The chess.Move to insert.
            comment: Optional comment to attach.
            starting_comment: Optional starting comment to attach.
            nags: Optional iterable of NAGs.

        Returns:
            The created ChildMoveNode.
        """
        child = ChildMoveNode(
            self,
            move,
            comment=comment,
            starting_comment=starting_comment,
            nags=nags,
        )
        if child in self.variations:
            self.variations.remove(child)
            self.variations.insert(0, child)
        return child


class ChildMoveNode(ChildNode):
    """Represent a PGN child move node with a cached board state.

    This node caches its board state after the move is pushed, preventing full-tree
    board recalculation during node traversal.
    """

    parent: Union[MoveNode, "ChildMoveNode"]  # pyright: ignore[reportIncompatibleVariableOverride]
    variations: List["ChildMoveNode"]  # pyright: ignore[reportIncompatibleVariableOverride]

    def __init__(
        self,
        parent: Union[MoveNode, "ChildMoveNode"],
        move: Move,
        *,
        comment: str = "",
        starting_comment: str = "",
        nags: Iterable[int] = (),
    ) -> None:
        """Initialize a child move node and cache the board after applying its move.

        Args:
            parent: The parent MoveNode or ChildMoveNode.
            move: The chess.Move representing this step.
            comment: Optional comment to attach.
            starting_comment: Optional starting comment to attach.
            nags: Optional iterable of NAGs.
        """
        super().__init__(parent, move, comment=comment, starting_comment=starting_comment, nags=nags)

        cached_parent_board = getattr(parent, "_cached_board", None)

        if cached_parent_board is not None:
            self._cached_board = cached_parent_board.copy()
        else:
            self._cached_board = parent.board()

        self._cached_board.push(move)

    def board(self) -> Board:
        """Return a copy of the cached board state after this move."""
        return self._cached_board.copy()

    def add_variation(
        self,
        move: Move,
        *,
        comment: str = "",
        starting_comment: str = "",
        nags: Iterable[int] = (),
    ) -> "ChildMoveNode":
        """Add a variation move node under this child node.

        Args:
            move: The chess.Move to add.
            comment: Optional comment to attach.
            starting_comment: Optional starting comment to attach.
            nags: Optional iterable of NAGs.

        Returns:
            The created ChildMoveNode.
        """
        child = ChildMoveNode(
            self,
            move,
            comment=comment,
            starting_comment=starting_comment,
            nags=nags,
        )
        return child

    def add_main_variation(
        self,
        move: Move,
        *,
        comment: str = "",
        starting_comment: str = "",
        nags: Iterable[int] = (),
    ) -> "ChildMoveNode":
        """Insert a main variation move node under this child node.

        Args:
            move: The chess.Move to insert.
            comment: Optional comment to attach.
            starting_comment: Optional starting comment to attach.
            nags: Optional iterable of NAGs.

        Returns:
            The created ChildMoveNode.
        """
        child = ChildMoveNode(
            self,
            move,
            comment=comment,
            starting_comment=starting_comment,
            nags=nags,
        )
        if child in self.variations:
            self.variations.remove(child)
            self.variations.insert(0, child)
        return child
