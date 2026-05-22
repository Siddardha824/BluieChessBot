from copy import deepcopy
from board.pieces import STARTING_POSITION

class GameState:
    def __init__(self):
        self.board = deepcopy(STARTING_POSITION)

        self.side_to_move = "white"

        self.move_history = []

    def make_move(self, from_square, to_square):

        if from_square == to_square:
            return

        start_row, start_col = from_square
        end_row, end_col = to_square

        piece = self.board[start_row][start_col]

        self.board[end_row][end_col] = piece
        self.board[start_row][start_col] = " "