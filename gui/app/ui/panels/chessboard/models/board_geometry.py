from dataclasses import dataclass
from typing import Optional
from PySide6.QtCore import QRect, QPointF

@dataclass
class BoardGeometry:
    board_size: int = 0
    square_size: int = 0
    x_offset: int = 0
    y_offset: int = 0
    flipped: bool = False

    def update(self, width: int, height: int) -> None:
        """
        Recalculates centering offsets and square dimensions.
        """
        # Keep the board square by taking the minimum dimension
        self.board_size = min(width, height)
        
        # Calculate size of a single square
        self.square_size = self.board_size // 8
        
        # Adjust board size to avoid rounding gaps
        self.board_size = self.square_size * 8
        
        # Centering offsets
        self.x_offset = (width - self.board_size) // 2
        self.y_offset = (height - self.board_size) // 2

    def square_to_rect(self, square_idx: int) -> QRect:
        """
        Converts a board index (0 = A8, 63 = H1) to QRect pixel bounds.
        """
        if not (0 <= square_idx < 64):
            raise ValueError(f"Square index {square_idx} is out of bounds (0-63).")
            
        row = square_idx // 8
        col = square_idx % 8
        
        if self.flipped:
            row = 7 - row
            col = 7 - col
            
        x = self.x_offset + col * self.square_size
        y = self.y_offset + row * self.square_size
        
        return QRect(x, y, self.square_size, self.square_size)

    def pixel_to_square(self, pos: QPointF) -> Optional[int]:
        """
        Converts local pixel coordinates to board index (0-63).
        Returns None if clicked outside board bounds.
        """
        x = pos.x()
        y = pos.y()
        
        board_x = x - self.x_offset
        board_y = y - self.y_offset
        
        if (board_x < 0 or board_x >= self.board_size or
            board_y < 0 or board_y >= self.board_size):
            return None
            
        col = int(board_x // self.square_size)
        row = int(board_y // self.square_size)
        
        col = min(7, max(0, col))
        row = min(7, max(0, row))
        
        if self.flipped:
            row = 7 - row
            col = 7 - col
            
        return row * 8 + col
