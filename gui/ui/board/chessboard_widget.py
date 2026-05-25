from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter, QColor
from PySide6.QtCore import Qt

class ChessBoard(QWidget):

    def __init__(self):
        super().__init__()

        self.setAutoFillBackground(True)
        self.setMinimumSize(400,400)
        self.setMaximumSize(640,640)

        self.selected_square = None

    def paintEvent(self, event):
        painter = QPainter(self)

        board_size = min(self.width(), self.height())
        square_size = board_size // 8

        for row in range(8):
            for col in range(8):
                color = QColor("#F0D9B5") if (row + col) % 2 == 0 else QColor("#B58863")

                painter.fillRect(
                    col * square_size,
                    row * square_size,
                    square_size,
                    square_size,
                    color
                )
        

    def mousePressEvent(self, event):
        pass
