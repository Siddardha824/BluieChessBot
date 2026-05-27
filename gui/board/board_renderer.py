# gui/board/board_renderer.py

from PySide6.QtGui import QPainter
from PySide6.QtCore import Qt
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .render_context import RenderContext

class BoardRenderer:
    def draw(self, painter: QPainter, context: "RenderContext") -> None:
        """
        Draws the alternating light and dark squares of the chessboard,
        and paints a sleek outer 1px border outline matching theme settings.
        """
        geom = context.geometry
        theme = context.theme
        
        painter.save()
        
        # 1. Paint Alternating light/dark squares
        for row in range(8):
            for col in range(8):
                is_light = (row + col) % 2 == 0
                color = theme.light_square if is_light else theme.dark_square
                
                x = geom.x_offset + col * geom.square_size
                y = geom.y_offset + row * geom.square_size
                
                painter.fillRect(x, y, geom.square_size, geom.square_size, color)
                
        # 2. Paint sleek outer board outline border matching other panels
        painter.setPen(theme.panel_border)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRect(geom.x_offset, geom.y_offset, geom.board_size - 1, geom.board_size - 1)
        
        painter.restore()
