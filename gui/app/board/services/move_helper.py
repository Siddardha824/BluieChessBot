"""Move helper utilities for working with UCI moves and board state conversions."""

from __future__ import annotations

import chess
from typing import TYPE_CHECKING

from gui.utils import get_logger

if TYPE_CHECKING:
    from ..models.board_state import BoardState

logger = get_logger(__name__)


class MoveHelper:
    """Utility helpers for making, undoing, and formatting chess moves."""

    @staticmethod
    def make_move(board: BoardState, move: str) -> bool:
        """Apply a UCI move to the board if the move is legal.

        Args:
            board: The current board state.
            move: A UCI move string, such as 'e2e4'.

        Returns:
            True if the move was applied successfully; False otherwise.
        """
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
        """Undo the last move on the board if possible.

        Args:
            board: The current board state.

        Returns:
            The UCI string of the undone move, or None if there was no move to undo.
        """
        if not board.is_start_pos:
            move = board.undo()
            if move is not None:
                logger.info("Move undone: %s", move.uci())
                return move.uci()

        logger.warning("Undo requested, but there are no moves to undo")
        return None

    @staticmethod
    def get_san_for_move(board: BoardState, uci_move: str) -> str:
        """Convert a UCI move into its SAN representation using the current board state.

        Args:
            board: The current board state.
            uci_move: A UCI move string, such as 'e2e4'.

        Returns:
            The SAN string for the move if valid, otherwise the original UCI string.
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
        """Format a sequence of UCI moves into a readable SAN move string.

        Args:
            board: The starting board state.
            uci_moves: A list of UCI move strings.

        Returns:
            A space-separated SAN move string, with move numbers included when possible.
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
