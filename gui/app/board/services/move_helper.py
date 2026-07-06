from __future__ import annotations

import chess
from typing import TYPE_CHECKING
from gui.utils import get_logger

if TYPE_CHECKING:
    from ..models.board_state import BoardState


logger = get_logger(__name__)


class MoveHelper:

    @staticmethod
    def make_move(board: BoardState, move: str) -> bool:
        try:
            chess_move = chess.Move.from_uci(move)
        except ValueError:
            logger.warning("Invalid UCI move string: %s", move)
            return False

        if board.is_legal(chess_move):
            board.move(chess_move)
            return True
        
        return False
    
    @staticmethod
    def undo_move(board: BoardState) -> str | None:
        if not board.is_start_pos:
            move = board.undo()
            if move is not None:
                logger.info("Move undone: %s", move.uci())
                return move.uci()

        logger.warning("Undo requested, but there are no moves to undo")
        return None
    
    @staticmethod
    def get_san_for_move(board: BoardState, uci_move: str) -> str:
        """
        Converts a single UCI move (e.g. 'e2e4') valid in the current board-state view
        into its SAN representation (e.g. 'e4').
        """

        try:
            move = chess.Move.from_uci(uci_move)
            if move in board.legal_moves:
                return board.san(move)
        except Exception as e:
            logger.debug("Failed to get SAN for move %s: %s", uci_move, e)

        return uci_move

    @staticmethod
    def format_uci_sequence(board: BoardState | chess.Board, uci_moves: list[str]) -> str:
        """
        Converts a list/sequence of UCI moves starting from the current board-state view
        into a formatted SAN string (e.g. '1. e4 e5 2. Nf3 Nc6').
        """
        if not uci_moves:
            return ""
        board = board.copy()
        san_moves = []

        for move_str in uci_moves:
            try:
                move = chess.Move.from_uci(move_str)
                if move in board.legal_moves:
                    san = board.san(move)
                    if board.turn == chess.WHITE:
                        san_moves.append(f"{board.fullmove_number}. {san}")
                    else:
                        if not san_moves:
                            san_moves.append(f"{board.fullmove_number}... {san}")
                        else:
                            san_moves.append(san)
                    board.push(move)
                else:
                    san_moves.append(move_str)
            except Exception as e:
                logger.debug("Failed to parse/format UCI move %s: %s", move_str, e)
                san_moves.append(move_str)

        return " ".join(san_moves)
