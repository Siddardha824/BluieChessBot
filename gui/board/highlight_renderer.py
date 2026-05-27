# gui/board/highlight_renderer.py

from PySide6.QtGui import QPainter, QPen
from PySide6.QtCore import Qt, QRect
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .render_context import RenderContext

class HighlightRenderer:
    def draw(self, painter: QPainter, context: "RenderContext") -> None:
        """
        Draws the active highlight overlays (selection, last move, check, and legal moves).
        """
        geom = context.geometry
        theme = context.theme
        hl = context.highlight_manager
        state = context.board_state
        
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        
        # Helper to get the screen QRect of a given C++ index
        def get_rect(sq: int) -> QRect:
            r = sq // 8
            c = sq % 8
            return QRect(
                geom.x_offset + c * geom.square_size,
                geom.y_offset + r * geom.square_size,
                geom.square_size,
                geom.square_size
            )

        # 1. Last Played Move Highlight (gold)
        if hl.last_move_from is not None:
            painter.fillRect(get_rect(hl.last_move_from), theme.last_move)
        if hl.last_move_to is not None:
            painter.fillRect(get_rect(hl.last_move_to), theme.last_move)

        # 2. Selected Square Highlight (off-white selection glow)
        if hl.selected_square is not None:
            painter.fillRect(get_rect(hl.selected_square), theme.selection)

        # 3. King in Check Highlight (soft red warning alert)
        if hl.check_square is not None:
            painter.fillRect(get_rect(hl.check_square), theme.check)

        # 4. Legal Move Indicators (dots for empty squares, rings for captures)
        for dest in hl.legal_moves:
            rect = get_rect(dest)
            center = rect.center()
            
            piece_at_dest = state.piece_at(dest)
            
            if piece_at_dest == '.':
                # Empty square: Draw a small filled circle in the center
                radius = geom.square_size * 0.15
                painter.setBrush(theme.legal_move)
                painter.setPen(Qt.PenStyle.NoPen)
                painter.drawEllipse(center, radius, radius)
            else:
                # Capture square: Draw a thick circular ring around the piece
                radius = geom.square_size * 0.43
                border_width = geom.square_size * 0.08
                
                pen = QPen(theme.legal_move)
                pen.setWidthF(border_width)
                pen.setStyle(Qt.PenStyle.SolidLine)
                
                painter.setPen(pen)
                painter.setBrush(Qt.BrushStyle.NoBrush)
                painter.drawEllipse(center, radius, radius)
                
        painter.restore()
