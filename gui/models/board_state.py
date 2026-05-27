# gui/models/board_state.py

from cmath import pi

import chess
from typing import List, Optional
from .move import Move

class BoardState:
    def __init__(self, fen: Optional[str] = None):
        """
        Initializes a BoardState wrapper around a chess.Board.
        
        Args:
            fen: Starting FEN string. If None, initializes standard starting position.
        """
        if fen:
            self._board = chess.Board(fen)
        else:
            self._board = chess.Board()

    @staticmethod
    def _convert_square(idx: int) -> int:
        """
        Converts between C++ engine indexing (0 = A8, 63 = H1)
        and python-chess indexing (0 = A1, 63 = H8).
        
        This mapping is self-inverse.
        """
        return (7 - (idx // 8)) * 8 + (idx % 8)

    def piece_at(self, cpp_idx: int) -> str:
        """
        Returns the piece character at the given C++ index ('P', 'n', etc.),
        or '.' if the square is empty.
        """
        pc_idx = self._convert_square(cpp_idx)
        piece = self._board.piece_at(pc_idx)
        if piece is None:
            return '.'
        return piece.symbol()

    def get_legal_moves(self, from_cpp_idx: int) -> List[int]:
        """
        Returns a list of legal destination C++ indices for a piece on `from_cpp_idx`.
        """
        from_pc_idx = self._convert_square(from_cpp_idx)
        legal_destinations = []
        
        for move in self._board.legal_moves:
            if move.from_square == from_pc_idx:
                legal_destinations.append(self._convert_square(move.to_square))
                
        return legal_destinations

    def is_legal(self, move: Move) -> bool:
        """
        Checks if a given Move is legal in the current position.
        """
        from_pc = self._convert_square(move.from_square)
        to_pc = self._convert_square(move.to_square)
        
        piece = self._board.piece_at(from_pc)

        if piece is None:
            return False

        # Determine if this move is a pawn promotion
        is_pawn = piece and piece.piece_type == chess.PAWN
        target_rank = chess.square_rank(to_pc)
        is_promotion_rank = (target_rank == 7 and piece.color == chess.WHITE) or \
                             (target_rank == 0 and piece.color == chess.BLACK)
        
        promotion_type = None
        if is_pawn and is_promotion_rank:
            # If no promotion piece was specified, default to Queen
            prom_char = move.promotion.lower() if move.promotion else 'q'
            prom_map = {'q': chess.QUEEN, 'r': chess.ROOK, 'b': chess.BISHOP, 'n': chess.KNIGHT}
            promotion_type = prom_map.get(prom_char, chess.QUEEN)
            
        pc_move = chess.Move(from_pc, to_pc, promotion=promotion_type)
        return pc_move in self._board.legal_moves

    def make_move(self, move: Move) -> bool:
        """
        Attempts to execute the move on the board.
        Returns True if successful, False if the move was illegal.
        """
        from_pc = self._convert_square(move.from_square)
        to_pc = self._convert_square(move.to_square)
        
        piece = self._board.piece_at(from_pc)

        if piece is None:
            return False

        # Determine if this move is a pawn promotion
        is_pawn = piece and piece.piece_type == chess.PAWN
        target_rank = chess.square_rank(to_pc)
        is_promotion_rank = (target_rank == 7 and piece.color == chess.WHITE) or \
                             (target_rank == 0 and piece.color == chess.BLACK)
        
        promotion_type = None
        if is_pawn and is_promotion_rank:
            # Default to Queen if not specified
            prom_char = move.promotion.lower() if move.promotion else 'q'
            prom_map = {'q': chess.QUEEN, 'r': chess.ROOK, 'b': chess.BISHOP, 'n': chess.KNIGHT}
            promotion_type = prom_map.get(prom_char, chess.QUEEN)
            
        pc_move = chess.Move(from_pc, to_pc, promotion=promotion_type)
        
        if pc_move in self._board.legal_moves:
            # Generate the algebraic notation (SAN) *before* pushing to board state
            san_string = self._board.san(pc_move)
            self._board.push(pc_move)
            return san_string
        return None

    def is_check(self) -> bool:
        """Returns True if the side to move is in check."""
        return self._board.is_check()

    def get_fen(self) -> str:
        """Returns the current board position as a FEN string."""
        return self._board.fen()

    def set_fen(self, fen: str):
        """Sets the board to the position described by the FEN string."""
        self._board.set_fen(fen)

    @property
    def turn(self) -> bool:
        """Returns True if it is White's turn, False for Black."""
        return self._board.turn

    def get_board_state_array(self) -> List[List[str]]:
        """
        Returns a 2D 8x8 list grid representation matching the legacy START_POS representation.
        Index [row][col] matches C++ indexing coordinates (Row 0 = A8-H8).
        """
        grid = []
        for r in range(8):
            row = []
            for f in range(8):
                cpp_idx = r * 8 + f
                row.append(self.piece_at(cpp_idx))
            grid.append(row)
        return grid
