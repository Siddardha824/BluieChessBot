import random

class ChessBot:
    def __init__(self):
        print('Bot started')
    
    def best_move(self, board):
        legal_moves = list(board.legal_moves)
        best_move = random.choice(legal_moves)

        return best_move