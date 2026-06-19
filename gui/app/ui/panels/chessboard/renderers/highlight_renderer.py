from PySide6.QtGui import QPainter, QPen, QColor, QPixmap
from PySide6.QtCore import Qt, QRect
from typing import TYPE_CHECKING
from gui.app.shared import ASSETS_DIR

if TYPE_CHECKING:
    from ..models.render_context import RenderContext

class HighlightRenderer:
    def __init__(self):
        self.win_pixmap = QPixmap(str(ASSETS_DIR / "Win.png"))
        self.loss_pixmap = QPixmap(str(ASSETS_DIR / "Loss.png"))
        self.draw_pixmap = QPixmap(str(ASSETS_DIR / "Draw.png"))
        self.resign_pixmap = QPixmap(str(ASSETS_DIR / "Resign.png"))

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
        
        # Helper to get the screen QRect of a given index
        def get_rect(sq: int) -> QRect:
            return geom.square_to_rect(sq)

        # 1. Last Played Move Highlight (gold/translucent)
        if hl.last_move_from is not None:
            color = QColor(theme.move_highlight)
            color.setAlpha(100)
            painter.fillRect(get_rect(hl.last_move_from), color)
        if hl.last_move_to is not None:
            color = QColor(theme.move_highlight)
            color.setAlpha(100)
            painter.fillRect(get_rect(hl.last_move_to), color)

        # 2. Selected Square Highlight (off-white selection glow)
        if hl.selected_square is not None:
            color = QColor(theme.selected_square)
            color.setAlpha(130)
            painter.fillRect(get_rect(hl.selected_square), color)

        # 3. King in Check Highlight (soft red warning alert)
        if hl.check_square is not None:
            color = QColor("#e53935")
            color.setAlpha(140)
            painter.fillRect(get_rect(hl.check_square), color)

        # 4. Legal Move Indicators (dots for empty squares, rings for captures)
        legal_move_color = QColor(theme.selected_square)
        legal_move_color.setAlpha(120)
        
        for dest in hl.legal_moves:
            rect = get_rect(dest)
            center = rect.center()
            
            # Map index to chess.Square to query piece presence
            from gui.app.board.services.board_mapper import BoardMapper
            sq = BoardMapper.index_to_square(dest)
            piece_at_dest = state.getBoard.piece_at(sq)
            
            if piece_at_dest is None:
                # Empty square: Draw a small filled circle in the center
                radius = geom.square_size * 0.15
                painter.setBrush(legal_move_color)
                painter.setPen(Qt.PenStyle.NoPen)
                painter.drawEllipse(center, radius, radius)
            else:
                # Capture square: Draw a thick circular ring around the piece
                radius = geom.square_size * 0.43
                border_width = geom.square_size * 0.08
                
                pen = QPen(legal_move_color)
                pen.setWidthF(border_width)
                pen.setStyle(Qt.PenStyle.SolidLine)
                
                painter.setPen(pen)
                painter.setBrush(Qt.BrushStyle.NoBrush)
                painter.drawEllipse(center, radius, radius)

        # 5. Debug Overlay Squares (translucent fills for attacks/legals)
        if hasattr(hl, "debug_overlay_squares") and hl.debug_overlay_squares:
            overlay_mode = getattr(hl, "debug_overlay_mode", "NONE")
            overlay_color = QColor(255, 179, 0, 80)  # Amber
            
            if "WHITE" in overlay_mode:
                overlay_color = QColor(0, 191, 165, 80)  # Emerald Teal
            elif "BLACK" in overlay_mode:
                overlay_color = QColor(239, 83, 80, 80)   # Crimson Red
            elif "ENGINE_LEGALS" in overlay_mode:
                overlay_color = QColor(124, 77, 255, 100) # Indigo
                
            for dest in hl.debug_overlay_squares:
                rect = get_rect(dest)
                painter.fillRect(rect, overlay_color)

        # 6. Game Over Outcome Badges (Win/Loss/Draw/Resign PNGs on Kings)
        if hasattr(hl, "game_over_result") and hl.game_over_result:
            import chess
            from gui.app.board.services.board_mapper import BoardMapper
            
            board = state.getBoard
            white_king_sq = board.king(chess.WHITE)
            black_king_sq = board.king(chess.BLACK)
            
            w_outcome = None
            b_outcome = None
            
            result = hl.game_over_result
            reason = getattr(hl, "game_over_reason", "")
            
            if result == "1-0":
                w_outcome = "win"
                b_outcome = "resign" if reason == "Resigned" else "loss"
            elif result == "0-1":
                w_outcome = "resign" if reason == "Resigned" else "loss"
                b_outcome = "win"
            elif result == "1/2-1/2":
                w_outcome = "draw"
                b_outcome = "draw"
                
            pixmaps = {
                "win": self.win_pixmap,
                "loss": self.loss_pixmap,
                "resign": self.resign_pixmap,
                "draw": self.draw_pixmap
            }
            
            for king_sq, outcome in [(white_king_sq, w_outcome), (black_king_sq, b_outcome)]:
                if king_sq is not None and outcome is not None:
                    king_idx = BoardMapper.coord_to_index(chess.square_name(king_sq))
                    rect = get_rect(king_idx)
                    
                    pixmap = pixmaps.get(outcome)
                    if pixmap and not pixmap.isNull():
                        badge_size = int(geom.square_size * 0.35)
                        badge_rect = QRect(
                            rect.right() - badge_size,
                            rect.top(),
                            badge_size,
                            badge_size
                        )
                        painter.drawPixmap(badge_rect, pixmap)
                
        painter.restore()
