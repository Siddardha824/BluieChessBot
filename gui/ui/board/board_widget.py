from PySide6.QtWidgets import QWidget
from PySide6.QtCore import QSize
from PySide6.QtGui import QPainter, QResizeEvent

from .board_renderer import BoardRenderer
from .piece_renderer import PieceRenderer
from gui.config import START_POS
from gui.debug import get_logger

logger = get_logger(__name__)

class ChessBoard(QWidget):

    def __init__(self, board_state = START_POS):
        super().__init__()

        self.setMinimumSize(400, 400)

        self.board_size = 0
        self.square_size = 0

        self.x_offset = 0
        self.y_offset = 0

        logger.info("Creating Board renderer")
        self.board_renderer = BoardRenderer(self)

        logger.info("Creating Piece renderer")
        self.piece_renderer = PieceRenderer(self)

        self.board_state = board_state
        self.selected_square = None

        logger.info("Chessboard initialized")

    def sizeHint(self):
        return QSize(640, 640)
    
    def resizeEvent(self, event):

        logger.info("Updating board Geometry")

        self.update_board_geometry()

        logger.info("Updating scaled piece images")

        self.piece_renderer.update_scaled_pieces()

        super().resizeEvent(event)

    def update_board_geometry(self):

        self.board_size = min(self.width(), self.height())

        self.square_size = self.board_size // 8

        self.x_offset = (self.width() - self.board_size) // 2

        self.y_offset = (self.height() - self.board_size) // 2

    def paintEvent(self, event):

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        self.board_renderer.draw_board(painter)

        self.piece_renderer.draw_pieces(painter)