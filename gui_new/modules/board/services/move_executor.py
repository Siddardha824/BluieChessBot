from __future__ import annotations

import chess
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..models.board_state import BoardState

class MoveExecutor:

    @staticmethod
    def make_move(board: BoardState, move: str) -> bool:
        try:
            chess_move = chess.Move.from_uci(move)
        except ValueError:
            return False

        board.push(chess_move)

        return True
    
    @staticmethod
    def undo_move(board: BoardState) -> str | None:
        if board.can_undo():
            move = board.pop()
            return move.uci()
