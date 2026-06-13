from ..templates import StyledWidget

class Chessboard(StyledWidget):
    def __init__(self, parent = None):
        super().__init__("chessboard", parent)

        self.draw_board()

    def draw_board(self):
        pass