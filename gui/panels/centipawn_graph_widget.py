# gui/panels/centipawn_graph_widget.py

from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QPolygonF
from PySide6.QtCore import QSize, Qt, QPointF
from gui.themes.theme_manager import theme_manager

class CentipawnGraphWidget(QWidget):
    def __init__(self, theme=None, parent=None):
        """
        Initializes the dynamic, painted Centipawn Advantage Graph.
        Plots evaluations move-by-move in a beautiful neon line chart.
        """
        super().__init__(parent)
        self.theme = theme if theme is not None else theme_manager.get_theme()
        self.history = [0.0]  # Start with an even game evaluation
        self.setMinimumHeight(100)
        self.setMaximumHeight(140)

    def add_score(self, cp: float) -> None:
        """Appends a new evaluation score and repaints the curve."""
        self.history.append(cp)
        # Limit history to the last 30 moves to keep the graph readable
        if len(self.history) > 30:
            self.history.pop(0)
        self.update()

    def update_score(self, cp: float) -> None:
        """Updates the active/last score in the current thinking thread."""
        if self.history:
            self.history[-1] = cp
            self.update()

    def clear(self) -> None:
        self.history = [0.0]
        self.update()

    def update_theme(self, theme) -> None:
        self.theme = theme
        self.update()

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.width()
        h = self.height()

        # Background fill
        bg_color = QColor(22, 17, 38, 70)  # Frosty dark glassmorphism
        painter.fillRect(0, 0, w, h, bg_color)

        # Border
        border_pen = QPen(self.theme.panel_border, 1)
        painter.setPen(border_pen)
        painter.drawRect(0, 0, w - 1, h - 1)

        # Draw Center baseline (0.0 even game)
        baseline_y = h / 2.0
        baseline_pen = QPen(QColor(255, 255, 255, 30), 1, Qt.PenStyle.DashLine)
        painter.setPen(baseline_pen)
        painter.drawLine(0, baseline_y, w, baseline_y)

        # Let's map evaluations from -4.0 (bottom) to +4.0 (top)
        # Y coordinate = center_y - (score * height_multiplier)
        if not self.history:
            return

        points = []
        n = len(self.history)
        x_step = w / float(max(1, n - 1))

        for idx, score in enumerate(self.history):
            # Clamp evaluation score to +/- 4.0
            clamped = max(-4.0, min(4.0, score))
            # Map score to Y coordinate: positive scores are up, negative are down
            y = baseline_y - (clamped * (h / 10.0))
            x = idx * x_step
            points.append(QPointF(x, y))

        # Draw filled gradient area under the curve
        if len(points) > 1:
            poly = QPolygonF()
            poly.append(QPointF(0, baseline_y))  # Start at baseline
            for pt in points:
                poly.append(pt)
            poly.append(QPointF(points[-1].x(), baseline_y))  # End at baseline
            
            # Gradient fill (Cyan glow transitioning to transparent purple)
            fill_brush = QBrush(QColor(0, 229, 255, 25))
            painter.setBrush(fill_brush)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawPolygon(poly)

        # Draw the curve line
        line_pen = QPen(self.theme.console_in, 2)  # Neon Cyan curve line
        painter.setPen(line_pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        for i in range(len(points) - 1):
            painter.drawLine(points[i], points[i+1])

        # Draw hot spots at node vertices
        spot_brush = QBrush(self.theme.console_out)  # Cosmic Purple dots
        painter.setBrush(spot_brush)
        painter.setPen(Qt.PenStyle.NoPen)
        for pt in points:
            painter.drawEllipse(pt, 3, 3)
