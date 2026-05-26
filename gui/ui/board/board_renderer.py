from PySide6.QtGui import QPainter, QColor

class BoardRenderer:
    def __init__(self, board):
        
        self.board = board


    def draw_board(self, painter):

        for row in range(8):
            for col in range(8):

                color = QColor("#F0D9B5") if (row + col) % 2 == 0 else QColor("#B58863")

                painter.fillRect(
                    self.board.x_offset + col * self.board.square_size,
                    self.board.y_offset + row * self.board.square_size,
                    self.board.square_size,
                    self.board.square_size,
                    color
                )