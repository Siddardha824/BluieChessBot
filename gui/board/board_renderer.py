# gui/board/board_renderer.py

from PySide6.QtGui import QPainter
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .render_context import RenderContext

class BoardRenderer:
    def draw(self, painter: QPainter, context: "RenderContext") -> None:
        """
        Draws the alternating light and dark squares of the chessboard.
        """
        geom = context.geometry
        theme = context.theme
        
        painter.save()
        for row in range(8):
            for col in range(8):
                is_light = (row + col) % 2 == 0
                color = theme.light_square if is_light else theme.dark_square
                
                x = geom.x_offset + col * geom.square_size
                y = geom.y_offset + row * geom.square_size
                
                painter.fillRect(x, y, geom.square_size, geom.square_size, color)
        painter.restore()
