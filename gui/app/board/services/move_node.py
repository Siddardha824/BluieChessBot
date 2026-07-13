from chess.pgn import Game, ChildNode
from chess import Move, Board
from typing import Iterable, Union, List, cast, Optional

class MoveNode(Game):
    variations: List["ChildMoveNode"] # pyright: ignore[reportIncompatibleVariableOverride]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._cached_board = super().board()

    def setup(self, board: Union[Board, str]) -> None:
        super().setup(board)
        self._cached_board = super().board()

    def board(self) -> Board:
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
    
    def add_variation(self, move: Move, *, comment: str = "", starting_comment: str = "", nags: Iterable[int] = ()) -> "ChildMoveNode":
        child = ChildMoveNode(self, move, comment=comment, starting_comment=starting_comment, nags=nags)
        self.variations.append(child)
        return child

    def add_main_variation(self, move: Move, *, comment: str = "", starting_comment: str = "", nags: Iterable[int] = ()) -> "ChildMoveNode":
        child = ChildMoveNode(self, move, comment=comment, starting_comment=starting_comment, nags=nags)
        self.variations.insert(0, child)
        return child


class ChildMoveNode(ChildNode):
    parent: Union[MoveNode, "ChildMoveNode"] # pyright: ignore[reportIncompatibleVariableOverride]
    variations: List["ChildMoveNode"] # pyright: ignore[reportIncompatibleVariableOverride]

    def __init__(self, parent: Union[MoveNode, "ChildMoveNode"], move: Move, *, comment: str = "", starting_comment: str = "", nags: Iterable[int] = ()) -> None:
        super().__init__(parent, move, comment=comment, starting_comment=starting_comment, nags=nags)
        
        cached_parent_board = getattr(parent, "_cached_board", None)
        
        if cached_parent_board is not None:
            self._cached_board = cached_parent_board.copy()
        else:
            self._cached_board = parent.board()
            
        self._cached_board.push(move)

    def board(self) -> Board:
        return self._cached_board.copy()

    def add_variation(self, move: Move, *, comment: str = "", starting_comment: str = "", nags: Iterable[int] = ()) -> "ChildMoveNode":
        child = ChildMoveNode(self, move, comment=comment, starting_comment=starting_comment, nags=nags)
        self.variations.append(child)
        return child

    def add_main_variation(self, move: Move, *, comment: str = "", starting_comment: str = "", nags: Iterable[int] = ()) -> "ChildMoveNode":
        child = ChildMoveNode(self, move, comment=comment, starting_comment=starting_comment, nags=nags)
        self.variations.insert(0, child)
        return child
