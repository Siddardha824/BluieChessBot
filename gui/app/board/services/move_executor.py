from __future__ import annotations

import chess
from typing import TYPE_CHECKING
from gui.utils import get_logger

if TYPE_CHECKING:
    from ..models.board_state import BoardState


logger = get_logger(__name__)


class MoveExecutor:

    @staticmethod
    def make_move(board: BoardState, move: str) -> bool:
        try:
            chess_move = chess.Move.from_uci(move)
        except ValueError:
            logger.warning("Invalid UCI move string: %s", move)
            return False

        board.push(chess_move)

        return True
    
    @staticmethod
    def undo_move(board: BoardState) -> str | None:
        if board.can_undo():
            move = board.pop()
            logger.info("Move undone: %s", move.uci())
            return move.uci()

        logger.warning("Undo requested, but there are no moves to undo")
        return None
