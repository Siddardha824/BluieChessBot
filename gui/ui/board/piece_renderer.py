from .sprite_manager import SpriteManager

class PieceRenderer:
    def __init__(self, board):
        
        self.board = board

        self.sprite_manager = SpriteManager()

        self.pieces = self.sprite_manager.pieces

    def draw_pieces(self, painter):
        scaled_pieces = self.sprite_manager.scaled_pieces
        square_size = self.board.square_size

        x_offset = self.board.x_offset
        y_offset = self.board.y_offset

        board_state = self.board.board_state

        row = 0
        
        for rank in board_state:
            col = 0

            for piece in rank:

                if piece != '.':
                    x = x_offset + col * square_size
                    y = y_offset + row * square_size
                    painter.drawPixmap(x, y, scaled_pieces[piece])

                col = col + 1

            row = row + 1

    def update_scaled_pieces(self):
        self.sprite_manager.update_scaled_pieces(self.board.square_size)
