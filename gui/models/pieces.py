# gui/models/pieces.py

# Piece color constants
WHITE = True
BLACK = False

# Piece type character constants (matching FEN representation)
PAWN = 'P'
KNIGHT = 'N'
BISHOP = 'B'
ROOK = 'R'
QUEEN = 'Q'
KING = 'K'

# Sets of white and black pieces for quick lookups
WHITE_PIECES = {'P', 'N', 'B', 'R', 'Q', 'K'}
BLACK_PIECES = {'p', 'n', 'b', 'r', 'q', 'k'}

def get_color(piece_char: str) -> bool | None:
    """Returns True for White, False for Black, and None for empty/invalid."""
    if piece_char in WHITE_PIECES:
        return WHITE
    elif piece_char in BLACK_PIECES:
        return BLACK
    return None

def is_opponent(piece_char_1: str, piece_char_2: str) -> bool:
    """Returns True if pieces are of different colors and both are valid pieces."""
    color1 = get_color(piece_char_1)
    color2 = get_color(piece_char_2)
    if color1 is None or color2 is None:
        return False
    return color1 != color2
