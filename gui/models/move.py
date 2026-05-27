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
