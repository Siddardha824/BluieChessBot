# gui/board/board_renderer.py

from PySide6.QtGui import QPainter, QFont
from PySide6.QtCore import Qt, QRect
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .board_widget import ChessBoard
    from .coordinate_helper import CoordinateHelper
    from gui.themes.default_theme import DefaultTheme

class BoardRenderer:
    def __init__(self, board: "ChessBoard", coord_helper: "CoordinateHelper", theme: "DefaultTheme"):
        """
        Initializes the BoardRenderer.
        
        Args:
            board: Reference to the ChessBoard QWidget.
            coord_helper: CoordinateHelper containing current board geometries.
            theme: Theme container exposing colors and fonts.
        """
        self.board = board
        self.coord_helper = coord_helper
        self.theme = theme

    def draw_board(self, painter: QPainter) -> None:
        """
        Draws the alternating light and dark squares of the chessboard.
        """
        for row in range(8):
            for col in range(8):
                square_idx = row * 8 + col
                rect = self.coord_helper.square_to_rect(square_idx)
                
                # Alternate square colors
                is_light = (row + col) % 2 == 0
                color = self.theme.light_square if is_light else self.theme.dark_square
                
                painter.fillRect(rect, color)

    def draw_coordinates(self, painter: QPainter) -> None:
        """
        Paints algebraic coordinates directly on the board.
        - Rank numbers (8 to 1) are drawn on the first column (File A / col 0).
        - File letters (a to h) are drawn on the bottom row (Rank 1 / row 7).
        """
        font = QFont(self.theme.font_family, self.theme.font_size, QFont.Weight.Bold)
        painter.setFont(font)
        
        # Files labels list (a-h)
        files = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
        
        for row in range(8):
            for col in range(8):
                square_idx = row * 8 + col
                rect = self.coord_helper.square_to_rect(square_idx)
                
                is_light = (row + col) % 2 == 0
                text_color = self.theme.text_on_light if is_light else self.theme.text_on_dark
                painter.setPen(text_color)
                
                # 1. Draw Rank Numbers (1-8) in the top-left of the first column
                if col == 0:
                    rank_num = str(8 - row)
                    # Add a padding offset so it draws slightly inside the top-left
                    padding = 3
                    label_rect = QRect(
                        rect.x() + padding,
                        rect.y() + padding,
                        rect.width() // 3,
                        rect.height() // 3
                    )
                    painter.drawText(label_rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop, rank_num)
                
                # 2. Draw File Letters (a-h) in the bottom-right of the last row
                if row == 7:
                    file_letter = files[col]
                    # Add a padding offset so it draws slightly inside the bottom-right
                    padding = 3
                    label_rect = QRect(
                        rect.x() + rect.width() - padding - rect.width() // 3,
                        rect.y() + rect.height() - padding - rect.height() // 3,
                        rect.width() // 3,
                        rect.height() // 3
                    )
                    painter.drawText(label_rect, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom, file_letter)

    def draw_highlights(self, painter: QPainter, highlight_manager, board_state) -> None:
        """
        Draws the active highlight overlays (selection, last move, check, and legal moves).
        """
        # 1. Last Move Highlight (source and destination)
        if highlight_manager.last_move_from is not None:
            from_rect = self.coord_helper.square_to_rect(highlight_manager.last_move_from)
            painter.fillRect(from_rect, self.theme.last_move)
        if highlight_manager.last_move_to is not None:
            to_rect = self.coord_helper.square_to_rect(highlight_manager.last_move_to)
            painter.fillRect(to_rect, self.theme.last_move)

        # 2. Selected Square Highlight
        if highlight_manager.selected_square is not None:
            sel_rect = self.coord_helper.square_to_rect(highlight_manager.selected_square)
            painter.fillRect(sel_rect, self.theme.selection)

        # 3. King in Check Highlight
        if highlight_manager.check_square is not None:
            check_rect = self.coord_helper.square_to_rect(highlight_manager.check_square)
            painter.fillRect(check_rect, self.theme.check)

        # 4. Legal Move Indicators
        for dest in highlight_manager.legal_moves:
            dest_rect = self.coord_helper.square_to_rect(dest)
            center = dest_rect.center()
            
            # Check if there is an opponent piece on the destination square (to show capture ring!)
            piece_at_dest = board_state.piece_at(dest)
            
            painter.save()
            painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
            
            if piece_at_dest == '.':
                # Empty square: Draw a small filled circle in the center
                radius = self.coord_helper.square_size * 0.15
                painter.setBrush(self.theme.legal_move)
                painter.setPen(Qt.PenStyle.NoPen)
                painter.drawEllipse(center, radius, radius)
            else:
                # Capture square: Draw a thick circular outline around the piece
                radius = self.coord_helper.square_size * 0.43
                border_width = self.coord_helper.square_size * 0.08
                
                # Import QPen to avoid name error if not already imported
                from PySide6.QtGui import QPen
                pen = QPen(self.theme.legal_move)
                pen.setWidthF(border_width)
                pen.setStyle(Qt.PenStyle.SolidLine)
                
                painter.setPen(pen)
                painter.setBrush(Qt.BrushStyle.NoBrush)
                painter.drawEllipse(center, radius, radius)
                
            painter.restore()

