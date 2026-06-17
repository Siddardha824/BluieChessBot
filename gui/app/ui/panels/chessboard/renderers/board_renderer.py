from PySide6.QtGui import QPainter, QColor
from PySide6.QtCore import Qt
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..models.render_context import RenderContext

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
        light_color = QColor(theme.board_light)
        dark_color = QColor(theme.board_dark)
        
        for row in range(8):
            for col in range(8):
                is_light = (row + col) % 2 == 0
                color = light_color if is_light else dark_color
                
                x = geom.x_offset + col * geom.square_size
                y = geom.y_offset + row * geom.square_size
                
                painter.fillRect(x, y, geom.square_size, geom.square_size, color)
                
        # 2. Paint sleek outer board outline border matching other panels
        border_color = dark_color.darker(130)
        painter.setPen(border_color)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRect(geom.x_offset, geom.y_offset, geom.board_size - 1, geom.board_size - 1)
        
        painter.restore()
