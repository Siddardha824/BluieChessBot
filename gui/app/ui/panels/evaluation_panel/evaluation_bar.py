from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter, QBrush, QColor, QPen

class EvaluationBar(QWidget):
    """
    Custom painted horizontal evaluation bar.
    Visualizes White's win percentage vs Black's win percentage.
    White is light color (left), Black is dark color (right), divided dynamically.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.win_chance = 0.5  # 0.0 to 1.0
        self.setFixedHeight(14)
        self.setObjectName("evaluationBar")

    def set_win_chance(self, chance: float):
        # Clip between 0.02 and 0.98 so at least a small line of both colors is visible
        self.win_chance = max(0.02, min(0.98, chance))
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        w = self.width()
        h = self.height()
        r = 6  # rounded corners radius
        
        # 1. Paint Background (Black's portion)
        painter.setBrush(QBrush(QColor("#2d2b27")))  # Sleek warm dark gray
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(0, 0, w, h, r, r)
        
        # 2. Paint White's portion
        white_width = int(w * self.win_chance)
        if white_width > 0:
            painter.setBrush(QBrush(QColor("#eaebeb")))  # Crisp off-white
            painter.drawRoundedRect(0, 0, white_width, h, r, r)
            # If partially filled, draw a rectangle connector to prevent rounding in the middle division
            if white_width < w:
                painter.drawRect(white_width - r, 0, r, h)
        
        # 3. Draw middle line (0.0 center point)
        painter.setPen(QPen(QColor("#d9534f"), 2, Qt.PenStyle.SolidLine))  # Muted crimson
        painter.drawLine(w // 2, 0, w // 2, h)
