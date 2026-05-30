# gui/widgets/evaluation_widget.py

from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel
from PySide6.QtCore import QSize, Qt, QRect
from PySide6.QtGui import QPainter, QColor, QFont

from gui.views.analysis.styles.analysis_styles import get_score_desc_style

class HorizontalEvalBar(QWidget):
    def __init__(self, theme, parent=None):
        super().__init__(parent)
        self.theme = theme
        self.setMinimumHeight(24)
        self.setMaximumHeight(32)
        
        self.evaluation = 0.0
        self.is_mate = False
        self.mate_in = 0
        self._font: QFont | None = None

    def sizeHint(self) -> QSize:
        return QSize(200, 28)

    def set_evaluation(self, cp_score: float, is_mate: bool = False, mate_in: int = 0) -> None:
        self.evaluation = max(-8.0, min(8.0, cp_score))
        self.is_mate = is_mate
        self.mate_in = mate_in
        self.update()

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        
        h = self.height()
        w = self.width()
        
        # Linear scale mapping [-8.0, +8.0] to [0.0, 1.0]
        ratio = (self.evaluation + 8.0) / 16.0
        
        # Left-to-right filling for horizontal bar: White on left, Black on right
        white_width = int(w * ratio)
        
        white_color = self.theme.eval_white
        black_color = self.theme.eval_black
        
        # 1. Paint Black's fill (right side)
        painter.fillRect(0, 0, w, h, black_color)
        
        # 2. Paint White's fill (left side)
        painter.fillRect(0, 0, white_width, h, white_color)
        
        # 3. Draw zero-balance center guideline
        painter.setPen(QColor(128, 128, 128, 120))
        painter.drawLine(w // 2, 0, w // 2, h)
        
        # 4. Draw bold text overlay
        painter.save()
        if self._font is None or self._font.families()[0] != self.theme.font_family:
            self._font = QFont(self.theme.font_family, 9, QFont.Weight.Black)
        painter.setFont(self._font)
        
        if self.is_mate:
            score_text = f"M{abs(self.mate_in)}"
            if self.mate_in < 0:
                score_text = f"-M{abs(self.mate_in)}"
            elif self.mate_in > 0:
                score_text = f"+M{abs(self.mate_in)}"
        else:
            score_text = f"{self.evaluation:+.2f}"
            
        # Text color is black on the white side, white on the black side
        is_white_advantaged = self.evaluation >= 0.0
        text_color = black_color if is_white_advantaged else white_color
        painter.setPen(text_color)
        
        # Define text boundary box snuggly aligned
        box_width = 70
        edge_padding = 10
        if is_white_advantaged:
            # Position text near the left (White side)
            text_rect = QRect(edge_padding, 0, box_width, h)
            align = Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        else:
            # Position text near the right (Black side)
            text_rect = QRect(w - edge_padding - box_width, 0, box_width, h)
            align = Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
            
        painter.drawText(text_rect, align, score_text)
        painter.restore()
        
        # 5. Draw sleek outer border outline matching theme panel borders
        painter.setPen(self.theme.panel_border)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRect(0, 0, w - 1, h - 1)

class EvaluationWidget(QWidget):
    def __init__(self, theme, parent=None):
        super().__init__(parent)
        self.theme = theme
        self._init_ui()

    def _init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)
        
        # 1. Left side: Sleek Horizontal Evaluation Bar instead of the big text
        self.eval_bar = HorizontalEvalBar(self.theme)
        layout.addWidget(self.eval_bar, stretch=2)
        
        # 2. Right side: Description of the advantage
        self.lbl_score_desc = QLabel("Balanced Even")
        self.lbl_score_desc.setStyleSheet(get_score_desc_style(self.theme))
        self.lbl_score_desc.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(self.lbl_score_desc, stretch=1)

    def set_evaluation(self, cp_score: float, is_mate: bool = False, mate_in: int = 0) -> None:
        """Sets evaluation score and description."""
        self.eval_bar.set_evaluation(cp_score, is_mate, mate_in)
        
        # Parse Description
        if is_mate:
            mate_val = mate_in if mate_in is not None else 0
            self.lbl_score_desc.setText("Forced Mate" if mate_val > 0 else "Forced Mated")
        else:
            if cp_score > 0.0:
                self.lbl_score_desc.setText("Better Advantage" if cp_score >= 1.0 else "Slightly Better")
            elif cp_score < 0.0:
                self.lbl_score_desc.setText("Worse Advantage" if cp_score <= -1.0 else "Slightly Worse")
            else:
                self.lbl_score_desc.setText("Balanced Even")

    def clear(self) -> None:
        """Resets the evaluation state to default."""
        self.eval_bar.set_evaluation(0.0, False, 0)
        self.lbl_score_desc.setText("Balanced Even")

    def update_theme(self, theme) -> None:
        self.theme = theme
        self.eval_bar.theme = theme
        self.eval_bar.update()
        self.lbl_score_desc.setStyleSheet(get_score_desc_style(self.theme))
