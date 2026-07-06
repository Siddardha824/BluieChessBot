from chess.pgn import Game, ChildNode, GameNode
from chess import Move, Board
from typing import Iterable, Union

class MoveNode(Game):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Initialize the cache with the default starting position
        self._cached_board = super().board()

    def setup(self, board: Union[Board, str]) -> None:
        super().setup(board)
        # Update the cached board whenever the root setup changes (e.g. load_fen)
        self._cached_board = super().board()

    def board(self) -> Board:
        # Return a copy to prevent external code from mutating the cache
        return self._cached_board.copy()

    @property
    def result(self) -> str:
        """Gets the current game result."""
        return self.headers.get("Result", "*")

    @result.setter
    def result(self, value: str) -> None:
        """Sets the game result (e.g., '1-0', '0-1', '1/2-1/2', '*')."""
        self.headers["Result"] = value

    @property
    def result_reason(self) -> str:
        """Gets the reason for the game result."""
        return self.headers.get("Termination", "")

    @result_reason.setter
    def result_reason(self, reason: str) -> None:
        """Sets the reason for the game result."""
        self.headers["Termination"] = reason

    def set_outcome(self, result: str, reason: str) -> None:
        """Convenience method to set both the result and the reason at once."""
        self.result = result
        self.result_reason = reason

    @property
    def white(self):
        """Gets the White Player"""
        return self.headers["White"]
    
    @white.setter
    def white(self, white_player: str):
        """Sets the White Player"""
        self.headers["White"] = white_player

    @property
    def black(self):
        """Gets the Black Player"""
        return self.headers["Black"]
    
    @black.setter
    def black(self, black_player: str):
        """Sets the Black Player"""
        self.headers["Black"] = black_player

    def add_variation(
        self,
        move: Move,
        *,
        comment: str = "",
        starting_comment: str = "",
        nags: Iterable[int] = (),
    ) -> "ChildMoveNode":
        child = ChildMoveNode(
            self,
            move,
            comment=comment,
            starting_comment=starting_comment,
            nags=nags,
        )
        self.variations.append(child)
        return child

    def add_main_variation(
        self,
        move: Move,
        *,
        comment: str = "",
        starting_comment: str = "",
        nags: Iterable[int] = (),
    ) -> "ChildMoveNode":
        child = ChildMoveNode(
            self,
            move,
            comment=comment,
            starting_comment=starting_comment,
            nags=nags,
        )
        self.variations.insert(0, child)
        return child


class ChildMoveNode(ChildNode):
    def __init__(
        self,
        parent: GameNode,
        move: Move,
        *,
        comment: str = "",
        starting_comment: str = "",
        nags: Iterable[int] = (),
    ) -> None:
        super().__init__(
            parent,
            move,
            comment=comment,
            starting_comment=starting_comment,
            nags=nags,
        )
        
        # Derive the cached board instantly from the parent's cache in O(1) time
        cached_parent_board = getattr(parent, "_cached_board", None)
        
        if cached_parent_board is not None:
            self._cached_board = cached_parent_board.copy()
        else:
            self._cached_board = parent.board() # Fallback for safety
            
        self._cached_board.push(move)

    def board(self) -> Board:
        # Return a copy to prevent external code from mutating the cache
        return self._cached_board.copy()

    def add_variation(
        self,
        move: Move,
        *,
        comment: str = "",
        starting_comment: str = "",
        nags: Iterable[int] = (),
    ) -> "ChildMoveNode":
        child = ChildMoveNode(
            self,
            move,
            comment=comment,
            starting_comment=starting_comment,
            nags=nags,
        )
        self.variations.append(child)
        return child

    def add_main_variation(
        self,
        move: Move,
        *,
        comment: str = "",
        starting_comment: str = "",
        nags: Iterable[int] = (),
    ) -> "ChildMoveNode":
        child = ChildMoveNode(
            self,
            move,
            comment=comment,
            starting_comment=starting_comment,
            nags=nags,
        )
        self.variations.insert(0, child)
        return child