# gui/board/coordinate_helper.py

from PySide6.QtCore import QRect, QPointF, QSize
from typing import Optional

class CoordinateHelper:
    def __init__(self, widget):
        """
        Initializes the Coordinate Helper with a reference to the QWidget.
        
        Args:
            widget: Reference to the parent ChessBoard QWidget.
        """
        self.widget = widget
        self.board_size = 0
        self.square_size = 0
        self.x_offset = 0
        self.y_offset = 0

    def update_geometry(self) -> None:
        """
        Recalculates the board bounds, square size, and centering offsets
        based on the parent widget's current width and height.
        """
        width = self.widget.width()
        height = self.widget.height()
        
        # Keep the board square by taking the minimum dimension
        self.board_size = min(width, height)
        
        # Calculate size of a single square (integer division)
        self.square_size = self.board_size // 8
        
        # Re-adjust board size to match exact grid boundaries to avoid rounding gaps
        self.board_size = self.square_size * 8
        
        # Center the board within the widget container
        self.x_offset = (width - self.board_size) // 2
        self.y_offset = (height - self.board_size) // 2

    def square_to_rect(self, square_idx: int) -> QRect:
        """
        Converts a C++ index (0 = A8, 63 = H1) to its corresponding QRect pixel bounds.
        """
        if not (0 <= square_idx < 64):
            raise ValueError(f"Square index {square_idx} is out of bounds (0-63).")
            
        row = square_idx // 8
        col = square_idx % 8
        
        x = self.x_offset + col * self.square_size
        y = self.y_offset + row * self.square_size
        
        return QRect(x, y, self.square_size, self.square_size)

    def pixel_to_square(self, pos: QPointF) -> Optional[int]:
        """
        Converts a local widget pixel coordinate (e.g. mouse position) 
        to its corresponding C++ board square index (0 = A8, 63 = H1).
        Returns None if the coordinates are outside the board boundaries.
        """
        x = pos.x()
        y = pos.y()
        
        board_x = x - self.x_offset
        board_y = y - self.y_offset
        
        # Return None if the position falls outside the board grid
        if (board_x < 0 or board_x >= self.board_size or
            board_y < 0 or board_y >= self.board_size):
            return None
            
        col = int(board_x // self.square_size)
        row = int(board_y // self.square_size)
        
        # Clamp to bounds just in case of float boundary edge cases
        col = min(7, max(0, col))
        row = min(7, max(0, row))
        
        return row * 8 + col
