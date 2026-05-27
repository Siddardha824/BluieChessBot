# gui/board/board_geometry.py

from dataclasses import dataclass

@dataclass
class BoardGeometry:
    board_size: int = 0
    square_size: int = 0
    x_offset: int = 0
    y_offset: int = 0
