# gui/panels/eval_bar_widget.py

from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter, QColor, QFont
from PySide6.QtCore import QSize, Qt, QRect

class EvalBarWidget(QWidget):
    def __init__(self, theme=None, parent=None):
        """
        Initializes the custom Painted vertical Evaluation Bar.
        Represents centipawn advantages dynamically, fully synchronized with active theme parameters.
        Optimized to a standard sleek, thin format (12-16px) with an extremely small, bold text overlay.
        """
        super().__init__(parent)
        self.setMinimumWidth(12)
        self.setMaximumWidth(18)
        
        from gui.themes.default_theme import DefaultTheme
        self.theme = theme if theme is not None else DefaultTheme()
        
        # Center represents 0.0 (even game)
        self.evaluation = 0.0
        self._font: QFont | None = None

    def sizeHint(self) -> QSize:
        return QSize(14, 400)

    def set_evaluation(self, cp_score: float) -> None:
        """
        Sets evaluation score (e.g. +1.50, -0.70) and triggers redraw.
        Score is clamped to represent a +/- 8 advantage dynamically.
        """
        self.evaluation = max(-8.0, min(8.0, cp_score))
        self.update()

    def paintEvent(self, event) -> None:
        """
        Custom painter draws White's advantage ratio (light fill) 
        vs Black's advantage ratio (dark fill) vertically.
        Renders an extremely small, bold score text overlay matching Lichess styling.
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        
        h = self.height()
        w = self.width()
        
        # Linear scale mapping [-8.0, +8.0] to [0.0, 1.0]
        ratio = (self.evaluation + 8.0) / 16.0
        
        # Invert ratio so positive scores (White) fill from top to bottom
        white_height = int(h * ratio)
        
        # Paint dynamic colors from active theme (no hardcoding!)
        white_color = self.theme.eval_white
        black_color = self.theme.eval_black
        
        # 1. Paint Black's fill (entire background first)
        painter.fillRect(0, 0, w, h, black_color)
        
        # 2. Paint White's fill (overlay from bottom up)
        painter.fillRect(0, h - white_height, w, white_height, white_color)
        
        # 3. Draw zero-balance center guideline
        painter.setPen(QColor(128, 128, 128, 120))
        painter.drawLine(0, h // 2, w, h // 2)
        
        # 4. Draw an extremely small, bold vertical/horizontal text displaying the score (e.g. "+1.4")
        painter.save()
        
        # Cache font config once - using a very small size (7pt) to fit perfectly inside the thin bar
        if self._font is None or self._font.families()[0] != self.theme.font_family:
            self._font = QFont(self.theme.font_family, 7, QFont.Weight.Black)  # Extra bold/black for legibility
        painter.setFont(self._font)
        
        score_text = f"{abs(self.evaluation):.1f}"
            
        # Draw text dynamically positioned depending on which side has the space!
        # If White is winning, the bottom half is white, so draw the score text near the bottom (in black text).
        # If Black is winning, the bottom half is black, so draw the score text near the top (in white text).
        is_white_advantaged = self.evaluation >= 0.0
        text_color = black_color if is_white_advantaged else white_color
        painter.setPen(text_color)
        
        # Define a text boundary box snuggly aligned near the edge
        edge_padding = 3
        box_height = 12
        if is_white_advantaged:
            # Position text near the bottom
            text_rect = QRect(0, h - edge_padding - box_height, w, box_height)
        else:
            # Position text near the top
            text_rect = QRect(0, edge_padding, w, box_height)
            
        # Draw centered and aligned horizontally, utilizing tight clipping
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, score_text)
        
        painter.restore()
        
        # 5. Draw sleek outer border outline matching theme panel borders
        painter.setPen(self.theme.panel_border)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRect(0, 0, w - 1, h - 1)
