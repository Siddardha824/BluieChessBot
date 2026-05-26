from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt

from gui.config import SPRITE_SHEET

class SpriteManager:

    def __init__(self):

        self.sheet = QPixmap(str(SPRITE_SHEET))

        self.piece_order = ('K', 'Q', 'B', 'N', 'R', 'P', 'k', 'q', 'b', 'n', 'r', 'p')

        self.pieces = {}
        self.scaled_pieces = {}

        self.load_pieces()

    def load_pieces(self):
        piece_width = self.sheet.width() // 6
        piece_height = self.sheet.height() // 2

        index = 0

        for row in range(2):
            for col in range(6):
                piece = self.sheet.copy(
                    col * piece_width,
                    row * piece_height,
                    piece_width,
                    piece_height
                )

                self.pieces[self.piece_order[index]]  = piece
                self.scaled_pieces[self.piece_order[index]]  = piece
                
                index = index + 1

    def update_scaled_pieces(self, square_size):
        for piece, pixmap in self.pieces.items():
            self.scaled_pieces[piece] = pixmap.scaled(
                square_size,
                square_size,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
    