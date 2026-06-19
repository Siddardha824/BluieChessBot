from PySide6.QtGui import QPainter, QFont, QColor
from PySide6.QtCore import Qt, QRect
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..models.render_context import RenderContext

class CoordinateRenderer:
    def __init__(self):
        """
        Initializes the CoordinateRenderer.
        Caches font configurations to prevent heap allocation inside hot rendering paths.
        """
        self._font: QFont | None = None

    def draw(self, painter: QPainter, context: "RenderContext") -> None:
        """
        Paints algebraic coordinates directly on the board.
        - Rank numbers (8 to 1) are drawn on the first column (File A / col 0).
        - File letters (a to h) are drawn on the bottom row (Rank 1 / row 7).
        """
        geom = context.geometry
        theme = context.theme
        
        painter.save()
        
        # Determine font configurations
        font_family = getattr(theme, "font_family", "Outfit")
        font_size = getattr(theme, "font_size", 10)
        
        # Cache font once to avoid dynamic allocations inside paint calls
        if self._font is None or self._font.families()[0] != font_family or self._font.pointSize() != font_size:
            self._font = QFont(font_family, font_size, QFont.Weight.Bold)
            
        painter.setFont(self._font)
        
        padding = 4
        
        light_color = QColor(theme.board_light)
        dark_color = QColor(theme.board_dark)
        
        # 1. Draw Rank Numbers (8 to 1) on the first column (col = 0, row from 0 to 7)
        for row in range(8):
            is_light = row % 2 == 0  # Column is 0, so light/dark alternates purely on row index
            text_color = dark_color if is_light else light_color
            painter.setPen(text_color)
            
            rank_num = str(row + 1) if geom.flipped else str(8 - row)
            rx = geom.x_offset + padding
            ry = geom.y_offset + row * geom.square_size + padding
            label_rect = QRect(rx, ry, geom.square_size // 3, geom.square_size // 3)
            
            painter.drawText(label_rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop, rank_num)
            
        # 2. Draw File Letters (a to h) on the bottom row (row = 7, col from 0 to 7)
        files = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
        for col in range(8):
            is_light = (7 + col) % 2 == 0  # Row is 7, so alternates based on (7 + col)
            text_color = dark_color if is_light else light_color
            painter.setPen(text_color)
            
            file_letter = files[7 - col] if geom.flipped else files[col]
            fx = geom.x_offset + col * geom.square_size
            fy = geom.y_offset + 7 * geom.square_size
            label_rect = QRect(
                fx + geom.square_size // 2,
                fy + geom.square_size // 2,
                geom.square_size // 2 - padding,
                geom.square_size // 2 - padding
            )
            
            painter.drawText(label_rect, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom, file_letter)
            
        painter.restore()
