"""PGN move node helpers with cached board state for efficient board reconstruction."""

from chess.pgn import Game, ChildNode
from chess import Move, Board
from typing import Iterable, Union, List


class MoveNode(Game):
    """A root PGN game node with cached board state and convenient metadata access."""

    variations: List["ChildMoveNode"]  # pyright: ignore[reportIncompatibleVariableOverride]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._cached_board = super().board()

    def setup(self, board: Union[Board, str]) -> None:
        """Set up the game from a board or FEN string and cache the board state."""
        super().setup(board)
        self._cached_board = super().board()

    def board(self) -> Board:
        """Return a copy of the cached board state for this game node."""
        return self._cached_board.copy()

    @property
    def result(self) -> str:
        """Get the current game result header."""
        return self.headers.get("Result", "*")

    @result.setter
    def result(self, value: str) -> None:
        """Set the game result header (e.g. '1-0', '0-1', '1/2-1/2', '*')."""
        self.headers["Result"] = value

    @property
    def result_reason(self) -> str:
        """Get the termination reason header for the game result."""
        return self.headers.get("Termination", "")

    @result_reason.setter
    def result_reason(self, reason: str) -> None:
        """Set the termination reason header for the game result."""
        self.headers["Termination"] = reason

    def set_outcome(self, result: str, reason: str) -> None:
        """Set both the game result and the termination reason in one call."""
        self.result = result
        self.result_reason = reason

    @property
    def white(self) -> str:
        """Get the name of the White player from the PGN headers."""
        return self.headers["White"]
    
    @white.setter
    def white(self, white_player: str) -> None:
        """Set the name of the White player in the PGN headers."""
        self.headers["White"] = white_player

    @property
    def black(self) -> str:
        """Get the name of the Black player from the PGN headers."""
        return self.headers["Black"]
    
    @black.setter
    def black(self, black_player: str) -> None:
        """Set the name of the Black player in the PGN headers."""
        self.headers["Black"] = black_player
    
    def add_variation(
        self,
        move: Move,
        *,
        comment: str = "",
        starting_comment: str = "",
        nags: Iterable[int] = (),
    ) -> "ChildMoveNode":
        """Add a variation move node as the next variation."""
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
        """Insert a variation move node as the main variation."""
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
    """A PGN child move node that caches its board after the move is applied."""

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
        """Initialize a child node and cache the board after applying its move."""
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
        """Add a variation move node under this child node."""
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
        """Insert a main variation move node under this child node."""
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
