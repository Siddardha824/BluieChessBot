# gui/models/move.py

class Move:
    def __init__(self, from_square: int, to_square: int, promotion: str | None = None):
        """
        Initializes a move container.
        
        Args:
            from_square: Integer from 0 (A8) to 63 (H1).
            to_square: Integer from 0 (A8) to 63 (H1).
            promotion: String character of the piece type (e.g. 'q', 'r') or None.
        """
        self.from_square = from_square
        self.to_square = to_square
        self.promotion = promotion

    def __repr__(self) -> str:
        promotion_str = f"={self.promotion}" if self.promotion else ""
        return f"Move({self.from_square} -> {self.to_square}{promotion_str})"

    def __eq__(self, other) -> bool:
        if not isinstance(other, Move):
            return False
        return (
            self.from_square == other.from_square
            and self.to_square == other.to_square
            and self.promotion == other.promotion
        )

    def __hash__(self) -> int:
        return hash((self.from_square, self.to_square, self.promotion))

    @staticmethod
    def from_uci(uci_str: str) -> 'Move':
        """
        Parses a standard UCI move string (e.g. 'e2e4' or 'e7e8q')
        and returns a Move object using C++ indexing (0 = A8).
        """
        if len(uci_str) < 4:
            raise ValueError(f"Invalid UCI move string: {uci_str}")
        
        from_col = ord(uci_str[0]) - ord('a')
        from_row = 8 - int(uci_str[1])
        to_col = ord(uci_str[2]) - ord('a')
        to_row = 8 - int(uci_str[3])
        
        from_square = from_row * 8 + from_col
        to_square = to_row * 8 + to_col
        
        promotion = uci_str[4] if len(uci_str) > 4 else None
        return Move(from_square, to_square, promotion)

